#!/usr/bin/env python3

import argparse
import typing
import unicodedata
from pathlib import Path
from xml.etree import ElementTree as ET

import tqdm

import bunkai.constant


def get_sentence(node) -> typing.Iterator[str]:
    if node.tag == "sentence":
        yield bunkai.constant.METACHAR_SENTENCE_BOUNDARY
    for luw in node:
        if luw.tag == "webBr":
            yield bunkai.constant.METACHAR_LINE_BREAK
            continue
        elif luw.tag.lower() != "luw":
            yield from get_sentence(luw)
            continue

        for fragment in luw:
            if fragment.tag in ["webBr", "br"]:
                yield bunkai.constant.METACHAR_LINE_BREAK
                continue
            elif fragment.tag.startswith("note"):
                continue
            elif fragment.tag in ["sampling", "fraction", "info"]:
                continue
            elif fragment.tag.lower() != "suw":
                raise NotImplementedError(fragment.tag)
            elif fragment.text is None:
                for unit in fragment:
                    if unit.tag == "sampling":
                        pass
                    elif unit.tag == "correction":
                        yield unit.get("originalText")
                    elif unit.tag not in [
                        "ruby",
                        "quote",
                        "enclosedCharacter",
                        "delete",
                        "subScript",
                        "superScript",
                    ]:
                        raise NotImplementedError(unit.tag)
                    else:
                        yield unit.text
                continue
            yield fragment.text


def operate_article(parent) -> typing.Iterator[str]:
    for node in parent:
        if node.tag in [
            "rejectedBlock",
            "info",
            "titleBlock",
            "abstract",
            "authorsData",
            "figureBlock",
        ]:
            continue
        elif node.tag in ["webBr", "br"]:
            yield bunkai.constant.METACHAR_LINE_BREAK
        elif node.tag == "sentence":
            yield from get_sentence(node)
        else:
            yield from operate_article(node)


def operation(data: str) -> typing.Iterator[str]:
    root = ET.fromstring(data)
    for child in root:
        if child.tag != "article":
            continue
        for i, t in enumerate(operate_article(child)):
            if i == 0:
                yield t.lstrip(bunkai.constant.METACHAR_SENTENCE_BOUNDARY)
            else:
                yield t
        yield "\n"


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, required=True)
    oparser.add_argument("--output", "-o", type=Path, required=True)
    oparser.add_argument("--nonfkc", action="store_true")
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    if opts.input.is_dir():
        opts.output.mkdir(exist_ok=True, parents=True)
        targets = [n for n in opts.input.iterdir()]
        for fname in tqdm.tqdm(targets, leave=False):
            with fname.open() as inf, opts.output.joinpath(f"{fname.stem}.txt").open("w") as outf:
                for string in operation(inf.read()):
                    if not opts.nonfkc:
                        string = unicodedata.normalize("NFKC", string)
                    outf.write(string)
    else:
        with opts.input.open() as inf, opts.output.open("w") as outf:
            for string in operation(inf.read()):
                if not opts.nonfkc:
                    string = unicodedata.normalize("NFKC", string)
                outf.write(string)


if __name__ == "__main__":
    main()
