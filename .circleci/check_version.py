#!/usr/bin/env python3

import argparse
from pathlib import Path

import toml

import bunkai


def operation(path_toml: Path, path_py: Path) -> None:
    with path_toml.open() as inf:
        pyproject = toml.load(inf)
        pyproject_version = pyproject["tool"]["poetry"]["version"]

    if pyproject_version != bunkai.__version__:
        raise KeyError("Version mismatch")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--toml", type=Path, required=True)
    oparser.add_argument("--py", type=Path, required=True)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(opts.toml, opts.py)


if __name__ == '__main__':
    main()
