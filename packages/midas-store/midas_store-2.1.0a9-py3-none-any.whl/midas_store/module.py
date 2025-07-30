"""MIDAS scenario upgrade module.

This module adds a mosaikhdf database to the scenario.

"""

import logging
from typing import cast

from midas.scenario.upgrade_module import ModuleParams, UpgradeModule
from midas.util.dict_util import set_default_bool, set_default_int

LOG = logging.getLogger(__name__)


class DatabaseModule(UpgradeModule):
    def __init__(self):
        super().__init__(
            module_name="store",
            default_scope_name="database",
            default_sim_config_name="MidasStore",
            default_import_str="midas_store.simulator:MidasCSVStore",
            default_cmd_str=("%(python)s -m midas_store.simulator %(addr)s"),
            log=LOG,
        )
        self.default_filename = "midas_store.csv"
        self._filename: str | None = None
        self._path: str | None = None
        self._unique_filename = False
        self._keep_old_files = False
        self._buffer_size: int = 1000
        self._timeout: int = 300

    def check_module_params(self, mp: ModuleParams):
        """Check module params for this upgrade."""

        mp.setdefault(self.default_scope_name, dict())
        mp.setdefault("filename", self.default_filename)
        mp.setdefault("path", self.scenario.base.output_path)
        set_default_bool(mp, "unique_filename", False)
        set_default_bool(mp, "keep_old_files", False)
        set_default_int(mp, "timeout", self._timeout)
        set_default_bool(mp, "in_process", False)  # Compatibility for Lasse
        set_default_bool(mp, "threaded", cast(bool, mp["in_process"]))
        set_default_int(mp, "buffer_size", self._buffer_size)

    def check_sim_params(self, mp: ModuleParams):
        self._simp_from_modulep(mp, "filename")
        self._simp_from_modulep(mp, "path")
        self._simp_from_modulep(mp, "unique_filename", dtype="bool")
        self._simp_from_modulep(mp, "keep_old_files", dtype="bool")
        self._simp_from_modulep(mp, "timeout", dtype="int")
        self._simp_from_modulep(mp, "threaded", dtype="bool")
        self._simp_from_modulep(mp, "buffer_size", dtype="int")

    def start_models(self):
        mod_key = "database"
        params = {
            "filename": cast(str, self.sim_params["filename"]),
            "path": cast(str, self.sim_params["path"]),
            "unique_filename": cast(bool, self.sim_params["unique_filename"]),
            "keep_old_files": cast(bool, self.sim_params["keep_old_files"]),
            "timeout": cast(int, self.sim_params["timeout"]),
            "threaded": cast(bool, self.sim_params["threaded"]),
        }
        filename = cast(str, params["filename"])
        if filename is not None and filename.endswith(".hdf5"):
            model = "DatabaseHDF5"
            params["buffer_size"] = cast(int, self.sim_params["buffer_size"])
        else:
            model = "DatabaseCSV"

        self.start_model(mod_key, model, params)

    def connect(self):
        pass

    def connect_to_db(self):
        pass
