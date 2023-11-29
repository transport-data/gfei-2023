Convert GFEI 2023 benchmarking data to SDMX
*******************************************

Convert
=======

    pip install -r requirements.txt
    python create.py

See file ``create.py`` for inline documentation.

The code generates six files:

- ``structure.xml`` —structural information.
- ``data-{FP,REG,SEC,WT}.xml`` —data for each data flow in SDMX-ML format.
- ``data-{FP,REG,SEC,WT}.csv`` —data for each data flow in SDMX-CSV format.
- ``all.zip`` —a ZIP archive containing all of the above.

The CSV and ZIP files are created only for convenience; the XML files are a
complete and explicit representation of the data, and the CSVs can be derived
from them trivially.

Using the data
==============

See `example.ipynb`_ and its inline comments.

Copyright and license
=====================
Code:
   Copyright © 2023 Paul Natsuo Kishimoto, Leonardo Paoli

   Licensed under the GNU General Public License version 3.0.
   https://www.gnu.org/licenses/gpl-3.0.en.html

Data:
   See https://doi.org/10.5281/zenodo.10148348
