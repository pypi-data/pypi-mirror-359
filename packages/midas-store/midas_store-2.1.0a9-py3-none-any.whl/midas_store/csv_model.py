import csv
import json
import logging
import multiprocessing as mp
import os
import queue
import threading
import traceback
from dataclasses import dataclass, field
from multiprocessing.context import SpawnProcess
from multiprocessing.synchronize import Event as MPEvent
from typing import Any, Callable, Union, cast
from uuid import uuid4

import numpy as np
from midas.util.dict_util import convert_val
from midas.util.runtime_config import RuntimeConfig
from mosaik.exceptions import SimulationError
from typing_extensions import TypeAlias

LOG = logging.getLogger(__name__)


AnyEvent: TypeAlias = Union[MPEvent, threading.Event]
DataDict: TypeAlias = dict[str, str | bool | int | float | None]
UPDATE: int = 0
STOP: int = 1
ERROR: int = -1


@dataclass
class QueueItem:
    code: int
    message: str = ""
    data: DataDict = field(default_factory=dict)


AnyQueue: TypeAlias = Union[mp.Queue, queue.Queue]


class CSVModel:
    def __init__(
        self,
        filename: str,
        *,
        path: str | None = None,
        unique_filename: bool = False,
        keep_old_files: bool = False,
        timeout: int = 300,
        threaded: bool = False,
        file_suffix: str = "csv",
    ) -> None:
        self._log = logging.getLogger(__name__)
        if path is None:
            path = RuntimeConfig().paths["output_path"]
            if path is None:
                path = ""
        os.makedirs(path, exist_ok=True)

        self.filename = os.path.abspath(os.path.join(path, filename))

        if self.filename and unique_filename:
            fp, suf = self.filename.rsplit(".", 1)
            self.filename = f"{fp}-{str(uuid4())}.{suf}"
        elif not self.filename:
            self.filename = f"midas-store-results-{str(uuid4())}.{file_suffix}"

        if keep_old_files:
            self._log.debug(
                "Keep_old_files is set to True. Attempting to find a unique "
                "filename for the database."
            )
            incr = 2
            new_filename = self.filename
            while os.path.exists(new_filename):
                fp, suf = self.filename.rsplit(".", 1)
                new_filename = f"{fp}_{incr:03d}.{suf}"
                incr += 1
            self.filename = new_filename
        elif os.path.exists(self.filename):
            os.rename(self.filename, f"{self.filename}.old")

        self._log.info("Saving results to database at '%s'.", self.filename)
        self._columns: list[str] = []
        self._data: DataDict = {}
        self._ctr: int = 0
        self._timeout: int = timeout

        self._lines_sent: int = 0
        self._threaded = threaded
        self._ctx = mp.get_context("spawn")
        self._io_proc: SpawnProcess | threading.Thread | None = None
        self._queue: AnyQueue
        self._result: AnyQueue
        self._writer_finished: AnyEvent
        self._soft_terminate: AnyEvent
        self._force_terminate: AnyEvent

        if self._threaded:
            self._queue = queue.Queue()
            self._result = queue.Queue()
            self._writer_finished = threading.Event()
            self._soft_terminate = threading.Event()
            self._force_terminate = threading.Event()
        else:
            self._queue = self._ctx.Queue()
            self._result = self._ctx.Queue()
            self._writer_finished = self._ctx.Event()
            self._soft_terminate = self._ctx.Event()
            self._force_terminate = self._ctx.Event()

    def to_memory(self, sid: str, eid: str, attr: str, val: Any) -> None:
        key = build_column_key(sid, eid, attr)
        self._data[key] = serialize(val)

    def step(self):
        if self._io_proc is None:
            self._columns = list(self._data)
            self._start_writer(run_writer)

        try:
            item = cast(QueueItem, self._result.get(block=False))
            if item.code == UPDATE:
                self._log.debug("Writer status: %s", item.message)
            else:
                msg = f"Writer finished unexpectedly early: {item.message}"
                raise SimulationError(msg)
        except queue.Empty:
            pass

        # if random.random() < 0.05:
        #     raise SimulationError("Random error")

        self._queue.put(QueueItem(code=UPDATE, data=self._data))
        self._lines_sent += 1

    def _start_writer(self, run_fnc: Callable) -> None:
        if self._threaded:
            self._io_proc = threading.Thread(
                target=run_fnc,
                args=(
                    self.filename,
                    self._columns,
                    self._queue,
                    self._result,
                    self._force_terminate,
                    self._writer_finished,
                ),
            )
            self._log.info("Starting file writer as thread ...")
        else:
            self._io_proc = self._ctx.Process(
                target=run_fnc,
                args=(
                    self.filename,
                    self._columns,
                    self._queue,
                    self._result,
                    self._force_terminate,
                    self._writer_finished,
                ),
            )
            self._log.info("Starting file writer as separate process ...")

        self._io_proc.start()

    def finalize(self):
        self._log.info("Shutting down the writer process ...")
        timeout = self._timeout
        if self._io_proc is None:
            self._log.info(
                "Writer is already None (likely was never initialized)."
            )
            if not self._threaded:
                cast(mp.Queue, self._result).close()
                cast(mp.Queue, self._queue).close()
        else:
            try:
                self._attempt_last_data()
                self._queue.put(QueueItem(code=STOP))
            except ValueError:
                self._log.debug("Queue was already closed.")

            self._log.info(
                "Waiting for writer to finish (%d items were sent)...",
                self._lines_sent,
            )
            while not self._writer_finished.is_set():
                try:
                    msg = cast(QueueItem, self._result.get(timeout=3))
                    timeout = self._timeout
                except queue.Empty:
                    self._log.info(
                        "Queue empty. Timeout in %d seconds", timeout
                    )
                    timeout -= 3
                    if timeout <= 0:
                        self._force_terminate.set()
                        break
                    continue

                if not self._threaded:
                    cast(mp.Queue, self._queue).cancel_join_thread()

                self._log.info("Writer status: %s", msg.message)

                if msg.code != UPDATE:
                    if msg.code == ERROR:
                        self._log.info("Writer terminated with error.")
                    break

            if not self._threaded:
                cast(mp.Queue, self._result).close()
                cast(mp.Queue, self._queue).close()

            self._io_proc.join()
            self._log.info("Writer finished!")

    def _attempt_last_data(self):
        pass


def run_writer(
    filename: str,
    fields: list[str],
    lines: AnyQueue,
    result: AnyQueue,
    force_terminate: AnyEvent,
    finished: AnyEvent,
):
    res_msg = QueueItem(code=STOP, message="Finished successfully.")
    batch_ctr = 0
    try:
        with open(filename, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()

        while True:
            if force_terminate.is_set():
                res_msg = QueueItem(
                    code=STOP,
                    message="Termination requested! Stopping immediately",
                )
                break
            try:
                item = cast(QueueItem, lines.get(timeout=1))
            except queue.Empty:
                continue
            except ValueError:
                res_msg = QueueItem(
                    code=ERROR, message="Queue was closed. Terminating!"
                )
                break

            if item.code == STOP:
                LOG.info("Received STOP. Terminating!")
                break

            with open(filename, "a", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields)
                writer.writerow(item.data)

            batch_ctr += 1
            if batch_ctr % 20 == 0:
                result.put(
                    QueueItem(
                        code=UPDATE, message=f"Processed {batch_ctr} items ..."
                    )
                )

    except Exception:
        res_msg = QueueItem(
            code=ERROR, message=f"Error writing csv: {traceback.format_exc()}"
        )
    except KeyboardInterrupt:
        res_msg = QueueItem(code=ERROR, message="Interrupted by user!")
    try:
        if res_msg.code == STOP and batch_ctr % 20 != 0:
            result.put(
                QueueItem(
                    code=UPDATE,
                    message=f"Processed {batch_ctr} items (finished)",
                )
            )
        result.put(res_msg)
    except ValueError:
        LOG.info("Result queue was already closed.")
    finished.set()


def build_column_key(sid, eid, attr) -> str:
    return f"{sid}.{eid}.{attr}"


def serialize(val):
    new_val = convert_val(val)

    if new_val == "MISSING_VALUE":
        if isinstance(val, (list, dict, np.ndarray)):
            return json.dumps(val)

    return new_val
