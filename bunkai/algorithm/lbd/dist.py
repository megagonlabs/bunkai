#!/usr/bin/env python3

import argparse
import json
import logging
import shutil
from pathlib import Path
from typing import List, Optional

import numpy as np
import torch
from transformers import BertForTokenClassification
from transformers.file_utils import cached_path

_NAME_UPDATER_DIR: str = 'up'
_NAME_UPDATER_LAYER_DIR: str = 'up_layer'
_DIST_VERSION: str = '1.1.0'
_NAME_VERSION: str = 'version.json'


def to_numpy(v):
    return v.to('cpu').detach().numpy().copy()


def to_tensor(v):
    return torch.from_numpy(v.astype(np.float32)).clone()


_COPY_FILES: List[str] =\
    ['added_tokens.json', 'special_tokens_map.json',
     'tokenizer_config.json', 'bunkai.json', 'labels.txt',
     'config.json']


def store_copy(path_in: Path, path_out: Path):
    for t in _COPY_FILES:
        shutil.copy2(path_in.joinpath(t), path_out.joinpath(t))


def store_updater(path_in: Path, base_model: str, path_out: Path):
    logging.disable(logging.WARN)
    orig_model = BertForTokenClassification.from_pretrained(base_model)
    new_model = BertForTokenClassification.from_pretrained(path_in)

    diffs_other_targets = [
        'bert.embeddings.word_embeddings.weight',
        'classifier.weight',
        'classifier.bias',
    ]
    path_out_up = path_out.joinpath(_NAME_UPDATER_DIR)
    path_out_up.mkdir(parents=True, exist_ok=True)
    for target in diffs_other_targets:
        orgv = to_numpy(eval(f'orig_model.{target}'))
        newv = to_numpy(eval(f'new_model.{target}'))
        if newv.shape != orgv.shape:
            if len(orgv.shape) == 2:
                z = np.zeros((newv.shape[0] - orgv.shape[0], orgv.shape[1]))
            elif len(orgv.shape) == 1:
                z = np.zeros((newv.shape[0] - orgv.shape[0],))
            else:
                raise NotImplementedError
            orgv = np.concatenate((orgv, z), axis=0)
        d = newv - orgv
        np.save(path_out_up.joinpath(f'{target}.npy'), d)

    diffs_layer_targets = [
        "attention.self.key.weight",
        "attention.self.key.bias",
        "intermediate.dense.weight",
        "intermediate.dense.bias",
        "output.dense.weight",
        "output.dense.bias",
    ]
    path_out_upl = path_out.joinpath(_NAME_UPDATER_LAYER_DIR)
    path_out_upl.mkdir(parents=True, exist_ok=True)
    for lidx, (orig_l, new_l) in enumerate(zip(orig_model.bert.encoder.layer, new_model.bert.encoder.layer)):
        _outdir_l: Path = path_out_upl.joinpath(f'{lidx}')
        _outdir_l.mkdir(parents=True, exist_ok=True)
        for target in diffs_layer_targets:
            d = to_numpy(
                eval(f'new_l.{target}') - eval(f'orig_l.{target}')
            )
            np.save(_outdir_l.joinpath(f'{target}.npy'), d)


def store_version(path_out: Path):
    with path_out.open('w') as outf:
        json.dump({'version': _DIST_VERSION}, outf, sort_keys=True)


def store(path_in: Path, path_out: Path) -> None:
    path_out.mkdir(parents=True, exist_ok=True)

    store_version(path_out.joinpath(_NAME_VERSION))
    store_copy(path_in, path_out)

    with path_in.joinpath('bunkai.json').open() as inf:
        base_model: Optional[str] = json.load(inf).get('base_model')
    if base_model is not None:
        store_updater(path_in, base_model, path_out)


def update(path_in: Path, base_model: str, path_out: Path):
    logging.disable(logging.WARN)
    orig_model = BertForTokenClassification.from_pretrained(base_model)

    for f in path_in.joinpath(_NAME_UPDATER_DIR).iterdir():
        target: str = f.name[:-len('.npy')]
#         print(f'Updating {target}')
        vals = np.load(f)
        orgv = to_numpy(eval(f'orig_model.{target}'))
        if len(orgv.shape) == 2:
            z = np.zeros((vals.shape[0] - orgv.shape[0], orgv.shape[1]))
        elif len(orgv.shape) == 1:
            z = np.zeros((vals.shape[0] - orgv.shape[0],))
        else:
            raise NotImplementedError

        orgv = np.concatenate((orgv, z), axis=0)
        orgv += vals
        orgv2 = torch.nn.Parameter(to_tensor(orgv))  # noqa: F841
        exec(f'orig_model.{target} = orgv2')

    for idx, orig_l, in enumerate(orig_model.bert.encoder.layer):
        for f in path_in.joinpath(_NAME_UPDATER_LAYER_DIR, f'{idx}').iterdir():
            target_l: str = f.name[:-len('.npy')]
#             print(f'Updating {target_l} in {idx}')
            vals = np.load(f)
            v = eval(f'orig_l.{target_l}')
            v2 = torch.nn.Parameter(  # noqa: F841
                to_tensor(
                    to_numpy(v) + vals
                )
            )
            exec(f'orig_l.{target_l} = v2')

    orig_model.save_pretrained(path_out)


def check_version(path_in: Path) -> bool:
    with path_in.open() as inf:
        version: str = json.load(inf).get('version', '')
    return version == _DIST_VERSION


def restore(path_in: Path, path_out: Path) -> None:

    if not check_version(path_in.joinpath(_NAME_VERSION)):
        raise KeyError

    path_out.mkdir(parents=True, exist_ok=True)

    with path_in.joinpath('bunkai.json').open() as inf:
        base_model: Optional[str] = json.load(inf).get('base_model')

    vocab_url: str = f"https://s3.amazonaws.com/models.huggingface.co/bert/{base_model}/vocab.txt"
    shutil.copy2(cached_path(vocab_url), path_out.joinpath('vocab.txt'))

    if base_model is not None:
        update(path_in, base_model, path_out)

    # config.json will be overwritten
    store_copy(path_in, path_out)


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, required=True)
    oparser.add_argument("--output", "-o", type=Path, required=True)
    oparser.add_argument("--restore", action='store_true')
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    if opts.restore:
        restore(opts.input, opts.output)
    else:
        store(opts.input, opts.output)


if __name__ == '__main__':
    main()
