
> [!WARNING]
> This project is an independent Python Port of the [Julia project](https://github.com/ITensor/ITensors.jl), still in its early stages. We are not officially affiliated with the [Flatiron Institute](https://www.simonsfoundation.org/flatiron/) nor the authors of ITensor.

![PyPI - Version](https://img.shields.io/pypi/v/itensors)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/itensors)
![PyPI - Format](https://img.shields.io/pypi/format/itensors)
![GitHub commit activity](https://img.shields.io/github/commit-activity/y/migueltorrescosta/itensors)



# Useful commands

## Installing he package

With pip:
```bash
pip install itensors
```

With poetry
```bash
poetry add itensors
```

## Setting up a development environment

After cloning the repo, run locally:
```bash
poetry install
```

## Running tests

WIP

## Publish new version to [PyPI](https://pypi.org/project/itensors/)

After updating the relevant version number on pyproject.toml, run the command below
```bash
poetry publish --build
```

# Design choices

We follow the ideology of the [original ITensor paper](https://www.scipost.org/SciPostPhysCodeb.4). In this section, we specify Python implementation choices, hopefully making the code clearer to follow. [Feedback and questions are welcomed](https://github.com/migueltorrescosta/itensors/issues)

## Structs

The key structures used are ITensor, Index, and TensorNetwork. We collocate these base structures under a single `itensors/struct.py file`.

