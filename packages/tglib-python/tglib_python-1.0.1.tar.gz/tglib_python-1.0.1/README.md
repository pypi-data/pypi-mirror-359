# Introduction to TGLib
TGLib is an open-source temporal graph library focusing on temporal distance and centrality
computations, and other local and global temporal graph statistics.

TGLib-Python is a pre-compiled, pre-built version of TGLib 1.5 which can be installed as a simple Python package.
No examples have been packaged with TGLib-Python, please get them from the official tglib repo below.

All credits go to the original authors at [https://gitlab.com/tgpublic/tglib](https://gitlab.com/tgpublic/tglib).

## Requirements

TGLib was compiled using:
   - Python 3.10
   - Ubuntu 22.04

Therefore, this package will not work on Windows or Mac and is untested for other Linux distros.

## Installation

```
pip install tglib-python
```

## Usage

Simply replace any usages of `pytglib` with `tglib-python`.

```
import tglib-python as tgl
tg = tgl.load_ordered_edge_list("your_tg_file.tg")
```

## License
TGLib is released under MIT license.
See [LICENSE.md](https://gitlab.com/tgpublic/tglib/-/blob/main/LICENSE.md?ref_type=heads) for details.

