Convert GFEI 2023 benchmarking data to SDMX
*******************************************

Usage: place the data file ``supplementary_information_gfei2023_tdc.xlsx`` in the same directory as this README.
Then::

    pip install -r requirements.txt
    python create.py

See file ``create.py`` for inline documentation.

The code generates two files:

- ``structure.xml`` —structural information.
- ``data.xml`` —data.