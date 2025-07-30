PARAMS = [
    "filename",
    "verbose",
    "path",
    "keep_old_files",
    "unique_filename",
    "threaded",
    "timeout",
]

META = {
    "type": "time-based",
    "models": {
        "DatabaseCSV": {
            "public": True,
            "any_inputs": True,
            "params": PARAMS,
            "attrs": [],
        },
        "DatabaseHDF5": {
            "public": True,
            "any_inputs": True,
            "params": PARAMS + ["buffer_size"],
            "attrs": [],
        },
    },
}
