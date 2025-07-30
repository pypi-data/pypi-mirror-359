# ourtils

[![Documentation Status](https://readthedocs.org/projects/ourtils/badge/?version=latest)](https://ourtils.readthedocs.io/en/latest/?badge=latest)

A collection of useful code for working with data.

## Install from pypi

```
$ pip install ourtils
```

## Dev Tips

This package uses `uv`. To run tests:

```
$ uv sync
$ uv run pytest
```

## Buildings docs locally

First make sure you have `make` installed, if you're on windows you can download it here: https://chocolatey.org/install

Then, create and activate a _new_ virtual environment using `requirements.txt` in the `docs/` directory. Then run this from inside the `docs` directory:
```
$ make clean html
```