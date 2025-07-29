# 🍇 Grapes Tokenizer

[![PyPI version](https://img.shields.io/pypi/v/grapes-tokenizer.svg)](https://pypi.org/project/grapes-tokenizer)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Build Status](https://github.com/akashpittalwar/Grapes-tokenizer/actions/workflows/ci.yml/badge.svg)](https://github.com/akashpittalwar/Grapes-tokenizer/actions)

---

**Grapes Tokenizer** is a lightweight, pure-Python library for converting text into deterministic, sum-based tokens. Originally designed for NLP research and LLM experiments, it offers a toy-friendly encoding scheme that:

* **Maps characters** to numeric values (letters, digits, and specials)
* **Applies positional weighting** to capture order information
* **Performs binary addition** of weighted values for a final single decimal token

While not suited for production subword tokenization, *Grapes Tokenizer* is perfect for exploring collision patterns, prompt engineering tricks, or integrating custom token schemes into larger pipelines.

## Table of Contents

* [Features](#features)
* [Installation](#installation)
* [Quick Start](#quick-start)
* [API Reference](#api-reference)

  * [`GrapesTokenizer`](#grapestokenizer)
* [Examples](#examples)

  * [Basic Encoding](#basic-encoding)
  * [Segment-and-Pack](#segment-and-pack)
* [Advanced Usage](#advanced-usage)
* [Development](#development)
* [Contributing](#contributing)
* [License](#license)

## Features

* 🔢 **Deterministic**: identical text always yields the same token
* ⚙️ **Positional Weighting**: retains order by multiplying each value by its index
* 🔣 **Full ASCII Support**: letters, digits, punctuation, whitespace
* ⚠️ **Non-reversible**: cannot reconstruct original text from token
* ⚠️ **Collisions Possible**: different strings may produce the same token
* 🚀 **Zero Dependencies**: pure Python 3.6+ implementation

## Installation

Install from PyPI:

```bash
pip install grapes-tokenizer
```

Or clone and install from source:

```bash
git clone https://github.com/akashpittalwar/Grapes-tokenizer.git
dcd Grapes-tokenizer
pip install -e .
```

## Quick Start

```python
from grapes_tokenizer import GrapesTokenizer

# Initialize the tokenizer (always positional weighting)
tok = GrapesTokenizer()

# Encode text to a single decimal token
print(tok.encode("cat"))    # → 65
print(tok.encode("tac"))    # → 31
print(tok.encode("!2872B")) # → 111
```

## API Reference

### `class GrapesTokenizer(case_sensitive: bool = False)`

Create a new tokenizer instance.

* **`case_sensitive`**: keep letter case (`True`) or normalize to lowercase (`False`, default).

#### Methods

##### `encode(text: str) -> int`

Converts the input string `text` to a single decimal token by:

1. Mapping each character:

   * `a–z` → `1–26`
   * `0–9` → `0–9`
   * others → `ord(ch)` (ASCII code)
2. Multiplying each value by its 1-based position index
3. Converting each result to binary and summing via binary addition
4. Returning the final sum as a decimal integer

```python
tok = GrapesTokenizer()
token = tok.encode("Hello, world!")
```

## Examples

### Basic Encoding

```python
>>> tok.encode("apple")
# Computation: a*1 + p*2 + p*3 + l*4 + e*5
```

### Segment-and-Pack

Split text into words, spaces, and punctuation, then encode each segment:

```python
import re
from grapes_tokenizer import GrapesTokenizer

def simple_segment(text):
    return re.findall(r"\w+|\s+|[^\w\s]", text)

def segment_and_pack(text):
    tok = GrapesTokenizer()
    return [tok.encode(seg) for seg in simple_segment(text)]

print(segment_and_pack("Hello World!"))
# → [0x48656c6c6f, 0x20, 0x576f726c64, 0x21]
```

## Advanced Usage

* **Case-sensitive mode**: preserve uppercase values
* **Custom mapping**: subclass `GrapesTokenizer` to override `_char_to_value`
* **Batch processing**: use list comprehensions or DataFrame apply for large corpora

## Development

1. Clone the repo
2. Create a virtual environment
3. Install dev dependencies:

   ```bash
   pip install -e .[dev]
   ```
4. Run tests:

   ```bash
   pytest
   ```
5. Build docs and distribution:

   ```bash
   python -m build
   ```

## Contributing

Contributions are welcome! Please open issues and pull requests on GitHub:

[https://github.com/akashpittalwar/Grapes-tokenizer](https://github.com/akashpittalwar/Grapes-tokenizer)

Please review `CONTRIBUTING.md` and adhere to the Apache 2.0 license.

## License

This project is licensed under the **Apache 2.0 License**. See [LICENSE](LICENSE) for details.
