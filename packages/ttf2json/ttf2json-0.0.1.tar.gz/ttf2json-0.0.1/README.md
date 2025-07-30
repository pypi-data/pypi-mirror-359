# ttf2json
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/ttf2json.svg)](https://badge.fury.io/py/ttf2json)
[![Tests](https://github.com/maslke/ttf2json/actions/workflows/tests.yml/badge.svg)](https://github.com/maslke/ttf2json/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/maslke/ttf2json/graph/badge.svg?token=Q3X8GM5ZWX)](https://codecov.io/gh/maslke/ttf2json)

This Python library allows you to convert .ttf font files into JSON format compatible with Three.js. It can be used via the command line or imported as a module in your Python code.


## Installation
You can install the package using pip:

```shell
pip install ttf2json
```

## How to use

### use via command line

1. Provide the font file path "ttf_file" and the output json file path "json_file". 

   ```shell
   python3 -m ttf2json --ttf_file ./msyh.ttf --json_file ./msyh.json
   ```

2. The "words" parameter can be optionally provided to convert only the necessary text and simplify the output json file. 

   ```shell
   python3 -m ttf2json --ttf_file ./msyh.ttf --json_file ./msyh.json --words abcdefg
   ```

3. The "words_from_file" parameter can be optionally provided to obtain the text to be converted from a file. When both the "words" parameter and the "words_from_file" parameter are provided, the "words_from_file" parameter will be ignored.

   ```shell
   python3 -m ttf2json --ttf_file ./msyh.ttf --json_file ./msyh.json --words_from_file ./words.txt
   ```

### imported as moudle


```python
from ttf2json import TTF2JSON

ttf2json = TTF2JSON("/path/to/ttf/file")
ttf2json.convert2json("words")
ttf2json.dump2json("/path/to/json/file")

```
   

