#!/usr/bin/env python3

import argparse
import json
import logging
import shutil
from pathlib import Path
from typing import List, Optional

import numpy as np
import torch
from transformers.models.auto.configuration_auto import AutoConfig
from transformers.models.bert.modeling_bert import BertForTokenClassification
from transformers.utils.hub import cached_file

_NAME_UPDATER_DIR: str = "up"
_DIST_VERSION: str = "1.1.0"
_NAME_VERSION: str = "version.json"


def to_numpy(v):
    return v.to("cpu").detach().numpy().copy()


def to_tensor(v):
    return torch.from_numpy(v.astype(np.float32)).clone()


_COPY_FILES: List[str] = [
    "added_tokens.json",
    "special_tokens_map.json",
    "tokenizer_config.json",
    "bunkai.json",
    "labels.txt",
    "config.json",
]


def store_copy(path_in: Path, path_out: Path):
    for t in _COPY_FILES:
        shutil.copy2(path_in.joinpath(t), path_out.joinpath(t))


def store_updater(path_in: Path, base_model: str, path_out: Path):
    logging.disable(logging.WARN)
    orig_model = BertForTokenClassification.from_pretrained(base_model)
    assert isinstance(orig_model, BertForTokenClassification)
    new_model = BertForTokenClassification.from_pretrained(path_in)
    assert isinstance(new_model, BertForTokenClassification)

    path_out_up = path_out.joinpath(_NAME_UPDATER_DIR)
    path_out_up.mkdir(parents=True, exist_ok=True)
    for target, _orgv in orig_model.named_parameters():
        orgv = to_numpy(_orgv)
        newv = to_numpy(new_model.state_dict()[target])
        if newv.shape != orgv.shape:
            if len(orgv.shape) == 2:
                z = np.zeros((newv.shape[0] - orgv.shape[0], orgv.shape[1]))
            elif len(orgv.shape) == 1:
                z = np.zeros((newv.shape[0] - orgv.shape[0],))
            else:
                raise NotImplementedError
            orgv = np.concatenate((orgv, z), axis=0)
        d = newv - orgv
        np.savez_compressed(path_out_up.joinpath(f"{target}.npz"), d)


def store_version(path_out: Path):
    with path_out.open("w") as outf:
        json.dump({"version": _DIST_VERSION}, outf, sort_keys=True)


def store(path_in: Path, path_out: Path) -> None:
    path_out.mkdir(parents=True, exist_ok=True)

    store_version(path_out.joinpath(_NAME_VERSION))
    store_copy(path_in, path_out)

    with path_in.joinpath("bunkai.json").open() as inf:
        base_model: Optional[str] = json.load(inf).get("base_model")
    if base_model is not None:
        store_updater(path_in, base_model, path_out)


def update(path_in: Path, base_model: str, path_out: Path):
    logging.disable(logging.WARN)
    orig_model = BertForTokenClassification.from_pretrained(base_model)
    assert isinstance(orig_model, BertForTokenClassification)

    osd = orig_model.state_dict()
    for f in path_in.joinpath(_NAME_UPDATER_DIR).iterdir():
        target: str = f.name[: -len(".npz")]
        vals = np.load(f)["arr_0"]
        orgv = to_numpy(osd[target])
        if len(orgv.shape) == 2:
            z = np.zeros((vals.shape[0] - orgv.shape[0], orgv.shape[1]))
        elif len(orgv.shape) == 1:
            z = np.zeros((vals.shape[0] - orgv.shape[0],))
        else:
            raise NotImplementedError

        orgv = np.concatenate((orgv, z), axis=0)
        orgv += vals
        orgv2 = torch.nn.Parameter(to_tensor(orgv))  # type: ignore
        osd[target] = orgv2

    new_model = BertForTokenClassification(config=AutoConfig.from_pretrained(path_in))
    new_model.load_state_dict(osd)  # type: ignore
    new_model.save_pretrained(path_out)  # type: ignore


def check_version(path_in: Path) -> bool:
    with path_in.open() as inf:
        version: str = json.load(inf).get("version", "")
    return version == _DIST_VERSION


def restore(path_in: Path, path_out: Path) -> None:
    if not check_version(path_in.joinpath(_NAME_VERSION)):
        raise KeyError

    path_out.mkdir(parents=True, exist_ok=True)

    with path_in.joinpath("bunkai.json").open() as inf:
        base_model: Optional[str] = json.load(inf).get("base_model")

    shutil.copy2(cached_file(base_model, "vocab.txt"), path_out.joinpath("vocab.txt"))  # type: ignore

    if base_model is not None:
        update(path_in, base_model, path_out)

    # config.json will be overwritten
    store_copy(path_in, path_out)


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, required=True)
    oparser.add_argument("--output", "-o", type=Path, required=True)
    oparser.add_argument("--restore", action="store_true")
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    if opts.restore:
        restore(opts.input, opts.output)
    else:
        store(opts.input, opts.output)


if __name__ == "__main__":
    main()
