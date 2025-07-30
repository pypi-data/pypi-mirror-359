import json
import logging
import queue
import time
import traceback
from typing import Any, cast

import numpy as np
import pandas as pd
from mosaik.exceptions import SimulationError
from typing_extensions import TypeAlias, override

from midas_store.csv_model import (
    ERROR,
    STOP,
    UPDATE,
    AnyEvent,
    AnyQueue,
    CSVModel,
    QueueItem,
    serialize,
)

LOG = logging.getLogger(__name__)

DataDictHdf: TypeAlias = dict[
    str, dict[str, list[str | bool | int | float | None]]
]


class HDF5Model(CSVModel):
    def __init__(
        self,
        filename: str,
        *,
        path: str | None = None,
        unique_filename: bool = False,
        keep_old_files: bool = False,
        buffer_size: int = 1000,
        threaded: bool = False,
        timeout: int = 300,
    ):
        super().__init__(
            filename,
            path=path,
            unique_filename=unique_filename,
            keep_old_files=keep_old_files,
            threaded=threaded,
            timeout=timeout,
            file_suffix="hdf5",
        )

        self._log = logging.getLogger(__name__)
        self._buffer_size = buffer_size
        self._buffer_ctr = 0
        self._columns_dict: dict[str, list[str]] = {}
        self._data_hdf: DataDictHdf = {}

    @override
    def to_memory(self, sid: str, eid: str, attr: str, val: Any) -> None:
        sid = sid.replace("-", "__")
        key = f"{eid}___{attr}".replace("-", "__")
        if self._columns_dict:
            if sid not in self._columns_dict:
                msg = f"Invalid sid detected: {sid}"
                self._buffer_ctr = 0
                raise ValueError(msg)

            if key not in self._columns_dict[sid]:
                msg = f"Invalid key detected for sid {sid}: {key}"
                self._buffer_ctr = 0
                raise ValueError(msg)

        self._data_hdf.setdefault(sid, {})
        self._data_hdf[sid].setdefault(key, [])

        if isinstance(val, (list, dict, np.ndarray)):
            val = json.dumps(val)
        elif isinstance(val, pd.DataFrame):
            val = val.to_json()
        else:
            val = serialize(val)
        self._data_hdf[sid][key].append(val)

    def step(self):
        if self._io_proc is None:
            self._start_writer(run_writer)

            for sid, keys in self._data_hdf.items():
                self._columns_dict[sid] = []
                for k in keys:
                    self._columns_dict[sid].append(k)

        try:
            item = cast(QueueItem, self._result.get(block=False))
            if item.code == UPDATE:
                self._log.debug("Writer status: %s", item.message)
            else:
                msg = f"Writer finished unexpectedly early: {item.message}"
                raise SimulationError(msg)
        except queue.Empty:
            pass

        self._buffer_ctr += 1
        self._lines_sent += 1

        if self._buffer_ctr >= self._buffer_size:
            dfs = {sid: pd.DataFrame(d) for sid, d in self._data_hdf.items()}
            self._queue.put(QueueItem(code=0, data=dfs))
            self._data_hdf = {}
            self._buffer_ctr = 0

    def _attempt_last_data(self):
        if self._buffer_ctr > 0:
            dfs = {sid: pd.DataFrame(d) for sid, d in self._data_hdf.items()}
            self._queue.put(QueueItem(code=0, data=dfs))


def run_writer(
    filename: str,
    fields: list[str],
    lines: AnyQueue,
    result: AnyQueue,
    force_terminate: AnyEvent,
    finished: AnyEvent,
):
    res_msg = QueueItem(code=1, message="Finished successfully.")
    append = False
    saved_rows = 0
    new_rows = 0

    try:
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

            for sid, data in item.data.items():
                new_rows = data.shape[0]
                data.index += saved_rows
                data.to_hdf(filename, key=sid, format="table", append=append)

            saved_rows += new_rows
            append = True
            result.put(
                QueueItem(
                    code=UPDATE, message=f"Processed {saved_rows} items ..."
                )
            )

    except Exception:
        res_msg = QueueItem(
            code=ERROR, message=f"Error writing hdf5: {traceback.format_exc()}"
        )
    except KeyboardInterrupt:
        res_msg = QueueItem(code=ERROR, message="Interrupted by user!")

    try:
        result.put(res_msg)
    except ValueError:
        LOG.info("Result queue was already closed.")
    finished.set()
