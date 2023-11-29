Convert GFEI 2023 benchmarking data to SDMX
*******************************************

Usage::

    pip install -r requirements.txt
    python create.py

See file ``create.py`` for inline documentation.

The code generates six files:

- ``structure.xml`` —structural information.
- ``data.xml`` —all data in SDMX-ML format.
- ``data-{FP,REG,SEC,WT}.csv`` —data for each measure in separate SDMX-CSV files.

TODO:

- [ ] Add an ``example.py`` to show how to read the files.
- [ ] Add UNIT_MEASURE attributes and code list.
- [ ] Automatically compress.
