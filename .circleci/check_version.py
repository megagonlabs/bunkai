#!/usr/bin/env python3

import argparse
from pathlib import Path

import toml


def operation(path_toml: Path, path_py: Path) -> None:
    with path_toml.open() as inf:
        pyproject = toml.load(inf)
        pyproject_version = pyproject["tool"]["poetry"]["version"]

    bunkai_version: str = ""
    with path_py.open() as inf:
        for line in inf:
            if line.startswith("__version_info__ ="):
                bunkai_version = ".".join([d.strip() for d in line.strip().split("(")[-1][:-1].split(",")])
                break

    if pyproject_version != bunkai_version:
        raise KeyError(f"Version mismatch: {pyproject_version} != {bunkai_version}")


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--toml", type=Path, required=True)
    oparser.add_argument("--py", type=Path, required=True)
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    operation(opts.toml, opts.py)


if __name__ == "__main__":
    main()
