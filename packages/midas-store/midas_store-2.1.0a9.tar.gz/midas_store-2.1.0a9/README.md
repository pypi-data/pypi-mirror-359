# Midas Store

## Description

This package contains a midas module providing a database simulator. 
This works like most other collectors for mosaik, i.e., it accepts any number of inputs and stores them in a database file.

Although this package is intended to be used with midas, you can use in any mosaik simulation scenario.

Version: 2.1

## Installation

This package will usually installed automatically together with `midas-mosaik` if you opt-in any of the extras, e.g., `base` or `bh`. 
It is available on pypi, so you can install it manually with

```bash
pip install midas-store
```

## Usage

The complete documentation is available at https://midas-mosaik.gitlab.io/midas.

### Inside of midas

To use the store inside of midas, just add `store` to your modules

```yaml
my_scenario:
  modules:
    - store
    - ...
```

and configure it with (`filename` is required, everything else is optional and can be left out if the default values, shown below, are used):

```yaml
  store_params:
    filename: my_results.csv
    step_size: 900
    unique_filename: False
    keep_old_files: False
```

All simulators that have something to store will then automatically connect to the `store` simulator.

### Any mosaik scenario

If you don't use midas, you can add the `store` manually to your mosaik scenario file. 
First, the entry in the `sim_config`:

```python
sim_config = {
    "MidasCSV": {"python": "midas_store.simulator:MidasCSVStore"},
    # ...
}
```

Next, you need to start the simulator (assuming a `step_size` of 900):

```python
store_sim = world.start("MidasCSVStore", step_size=900)
```

Finally, the model needs to be started:

```python
store = store_sim.Database(filename="my_results.csv", keep_old_files=False, unique_filename=False)
```

Afterwards, you can define `world.connect(other_entity, store, attrs)` as you like.

## License

This software is released under the GNU Lesser General Public License (LGPL). See the license file for more information about the details.