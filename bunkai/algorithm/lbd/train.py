#!/usr/bin/env python3

import argparse
import dataclasses
import json
import sys
import typing
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from torch import nn
from torch.utils.data.dataset import Dataset

from bunkai.algorithm.lbd.corpus import LABEL_NSEP, LABEL_OTHER, LABEL_SEP
from bunkai.base.annotation import Tokens
from bunkai.third.utils_ner import InputFeatures, convert_examples_to_features


def convert(datapath: Path, data_dir: Path, name: str):
    train_data_path = data_dir.joinpath(f"{name}.txt")
    with datapath.open() as inf, train_data_path.open("w") as outf:
        outf.write("-DOCSTART-\n")
        for line in inf:
            tokens = Tokens.from_json(line)
            for idx, span in enumerate(tokens.spans):
                outf.write(f"{span} {tokens.labels[idx]}\n")
            outf.write("\n")


@dataclasses.dataclass
class BunkaiConfig(DataClassJsonMixin):
    max_seq_length: int
    base_model: str


def prepare_config(
    train_path: Path,
    dev_path: Path,
    modelpath: Path,
    max_seq_length: int,
    base_model: str,
    num_train_epochs: int,
) -> Path:
    json_config = {
        "data_dir": "",
        "labels": "",
        "output_dir": "",
        "model_name_or_path": base_model,
        "max_seq_length": max_seq_length,
        "num_train_epochs": num_train_epochs,
        "per_device_train_batch_size": 32,
        "save_steps": 750,
        "seed": 1,
        "do_train": True,
        "do_eval": False,
        "do_predict": False,
        "overwrite_output_dir": True,
        "overwrite_cache": True,
    }

    modelpath.mkdir(exist_ok=True, parents=True)
    path_config_json = modelpath.joinpath("config.json")

    data_dir = modelpath.joinpath("data")
    data_dir.mkdir(exist_ok=True, parents=True)

    out_dir = modelpath.joinpath("out")
    out_dir.mkdir(exist_ok=True, parents=True)

    label_path = out_dir.joinpath("labels.txt")
    with out_dir.joinpath("bunkai.json").open("w") as f:
        json.dump(
            BunkaiConfig(
                base_model=base_model,
                max_seq_length=max_seq_length,
            ).to_dict(),
            f,
            indent=4,
            sort_keys=True,
        )

    json_config["data_dir"] = str(data_dir.absolute())
    json_config["labels"] = str(label_path.absolute())
    json_config["output_dir"] = str(out_dir.absolute())

    with path_config_json.open("w") as f:
        json.dump(json_config, f, indent=4, sort_keys=True)
    with label_path.open("w") as f:
        f.write(f"{LABEL_OTHER}\n{LABEL_SEP}\n{LABEL_NSEP}\n")

    convert(train_path, data_dir, "train")
    if dev_path is not None:
        convert(dev_path, data_dir, "dev")
    return path_config_json


def train(
    train_path: Path,
    dev_path: Path,
    modelpath: Path,
    max_seq_length: int,
    base_model: str,
    num_train_epochs: int,
):
    path_config_json = prepare_config(train_path, dev_path, modelpath, max_seq_length, base_model, num_train_epochs)
    sys.argv = ["", str(path_config_json)]
    import bunkai.third.run_ner

    bunkai.third.run_ner.main()


class MyDataset(Dataset):
    features: typing.List[InputFeatures]
    pad_token_label_id: int = nn.CrossEntropyLoss().ignore_index

    def __len__(self):
        return len(self.features)

    def __getitem__(self, i) -> InputFeatures:
        return self.features[i]

    def __init__(self, examples, labels, max_seq_length: int, tokenizer, is_xlnet: bool):
        self.features = convert_examples_to_features(
            examples,
            labels,
            max_seq_length,
            tokenizer,
            cls_token_at_end=is_xlnet,
            # xlnet has a cls token at the end
            cls_token=tokenizer.cls_token,
            cls_token_segment_id=2 if is_xlnet else 0,
            sep_token=tokenizer.sep_token,
            pad_on_left=bool(tokenizer.padding_side == "left"),
            pad_token=tokenizer.pad_token_id,
            pad_token_segment_id=tokenizer.pad_token_type_id,
            pad_token_label_id=self.pad_token_label_id,
        )


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, required=True)
    oparser.add_argument("--dev", type=Path)
    oparser.add_argument("--model", "-m", type=Path, required=True)
    oparser.add_argument("--seq", default=320, type=int)
    oparser.add_argument("--epoch", default=30, type=int)
    oparser.add_argument(
        "--base",
        default="bandainamco-mirai/distilbert-base-japanese",
        choices=[
            "cl-tohoku/bert-base-japanese-whole-word-masking",
            "bandainamco-mirai/distilbert-base-japanese",
        ],
    )
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()

    train(
        train_path=opts.input,
        dev_path=opts.dev,
        modelpath=opts.model,
        max_seq_length=opts.seq,
        base_model=opts.base,
        num_train_epochs=opts.epoch,
    )


if __name__ == "__main__":
    main()
