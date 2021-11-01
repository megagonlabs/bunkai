#!/usr/bin/env python3

import argparse
import dataclasses
import json
import typing
import unicodedata

import bunkai.constant


@dataclasses.dataclass
class DoccanoDataObject:
    annotation_id: int
    text: str
    labels: typing.List[typing.Tuple[int, int, str]]
    meta: typing.Dict[str, typing.Any]


def sbd(dobj: DoccanoDataObject) -> typing.Iterator[str]:
    __start_index = 0
    labels_sequence = sorted(
        [label_tuple for label_tuple in dobj.labels if label_tuple[2] == "SEP" or label_tuple[2].startswith("SEP-")],
        key=lambda t: t[0],
    )
    for label_tuple in labels_sequence:
        yield dobj.text[__start_index : label_tuple[1]]
        __start_index = label_tuple[1]

    if __start_index != len(dobj.text) - 1:
        yield dobj.text[__start_index:]


def operation(data: dict) -> typing.Iterator[str]:
    dobj = DoccanoDataObject(
        annotation_id=data["id"],
        text=data["text"],
        labels=data["labels"],
        meta=data["meta"],
    )
    for text_part in sbd(dobj):
        if len(text_part) > 0:
            yield text_part


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=argparse.FileType("r"), default="-", required=True)
    oparser.add_argument("--output", "-o", type=argparse.FileType("w"), default="-")
    oparser.add_argument("--nonfkc", action="store_true")
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    with opts.input as inf, opts.output as outf:
        for line in inf:
            data = json.loads(line)
            for __i, string in enumerate(operation(data)):
                if __i > 0:
                    outf.write(bunkai.constant.METACHAR_SENTENCE_BOUNDARY)
                if not opts.nonfkc:
                    string = unicodedata.normalize("NFKC", string)
                outf.write(string)
            outf.write("\n")


if __name__ == "__main__":
    main()
