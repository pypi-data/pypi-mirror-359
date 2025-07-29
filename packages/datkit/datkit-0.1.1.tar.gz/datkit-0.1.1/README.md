[![Unit tests](https://github.com/myokit/datkit/actions/workflows/unit-tests-ubuntu.yml/badge.svg)](https://github.com/myokit/datkit/actions/workflows/unit-tests-ubuntu.yml)
[![Documentation](https://readthedocs.org/projects/datkit/badge/?version=latest)](https://datkit.readthedocs.io/?badge=latest)

# Datkit

This module contains some simple methods that are useful when analysing time 
series data.

The code is tested on a recent version of Ubuntu & Python 3, but is so simple
that it should work everywhere else too.

## Installation

To install the latest release from PyPI, use

```
pip install datkit
```

## Installation for development

To install from the repo, use e.g.
```
python setup.py install -e .
```

Tests can then be run with
```
python -m unittest
```

And docs can be built with
```
cd docs
make clean html
```
