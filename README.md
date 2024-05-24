# Armenian patents data
This is a dataset of armenian patents, parsed from [AIPO website](https://aipo.am/en/search-int-classification), as well as code which generates it.
This project is dedicated to [@opendataam](https://github.com/opendataam) team, specifically [this task](https://github.com/opendataam/opendatam-tasks/issues/26).
It's not in development right now, and there might be some bugs.

## Setup
Virtual environment is planned, but not supported right now, so you will need an environment which supports these dependencies, with python version being at least 3.10 (3.12 is recommended):
```python3
import itertools
import json
import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
```
Other than that, you should have these 2 files in the same directory:
- main.py
- aipoparser.py

`aipoparser` can be used as a module on its own.

This file (ICID codes.json) is compiled manually and consists of every ICID code from [this website](https://locpub.wipo.int/enfr/?class_number=1&explanatory_notes=hide&id_numbers=hide&lang=en&menulang=en&mode=loc&notion=&version=20250101), it greatly helps with parsing efficiency
- data/
  - ICID codes.json

Finally, just run `main.py`, user interface will guide you from there.

## Overview
Currently, all code is organized in a `aipoparser` module. This code does not contain comments **right now**, so here's a quick overview:
### Context
[This AIPO webpage](https://aipo.am/en/search-int-classification) allows everyone to search for registred armenian patents according to some filter. 
There seems to be no way of getting every entry at once, so we need a way to extract it.
Author of [this task](https://github.com/opendataam/opendatam-tasks/issues/26) recommeds using ICID codes (International Classification of Industrial Designs).
### Functions
1. `aipo_request(...)` makes an HTTP request for patents exactly as AIPO webpage does.
2. `get_patent_by_id(...)` parses a request for individual certificate id to python `dict` object.
3. `get_group_by_icid_code(...)` parses a request for specific ICID code to python nested `dict` object.
4. `generate_icid_codes()` returns a generator for looping over ICID codes.
5. `get_ICID_json(...)` requests patents for every ICID code and stores them in corresponding ICID.json file
6. `fix_patents_list(...)` turns unordered list of patents with dublicates and missing entries to perfectly sorted list with unique entries without gaps. In theory should just download every patent one by one if empty array is passed, but I did not test.
7. `get_all_patents(...)` gets a list of patents from ICID.json, then "fixes" it, stores it in corresponding patents.json file
8. `get_all_info_for_patent(...)` requests detailed information about specific patent from AIPO, returns a parsed dictionary with all info
9. `get_all_info(...)` requests detailed information for every patent in patents.json, stores it in corresponding all_info.json

## Collaboration
If somebody for some reason wants to contribute to this mess, open an issue and fork this repo.
This project is under an MIT license, so use it as you wish
