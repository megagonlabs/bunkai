#!/usr/bin/env python3

import argparse
import json
import re
import typing

try:
    from seqeval.metrics import performance_measure
except ImportError:
    raise Exception("You need to install bunkai with pip install -U bunkai[train]")

from bunkai.constant import METACHAR_LINE_BREAK, METACHAR_SENTENCE_BOUNDARY

REGEXP_SB_WITH_BLANKS_SPAN: str = f"({METACHAR_SENTENCE_BOUNDARY})([\\s{METACHAR_LINE_BREAK}]*)"
RE_SB_WITH_BLANKS_SPAN = re.compile(REGEXP_SB_WITH_BLANKS_SPAN)
RE_SBS_SPAN = re.compile(f"{METACHAR_SENTENCE_BOUNDARY}+")


def get_bo(text: str, lbonly: bool) -> typing.List[str]:
    """Get a list of BIO sequence from input text."""
    assert METACHAR_SENTENCE_BOUNDARY + METACHAR_SENTENCE_BOUNDARY not in text
    assert not text.startswith(METACHAR_SENTENCE_BOUNDARY)
    ret: typing.List[str] = []
    exist_under_bar: bool = False
    for char in text:
        if char == METACHAR_SENTENCE_BOUNDARY:
            if lbonly and exist_under_bar is False:
                continue
            else:
                ret[-1] = "SEP"
                exist_under_bar = False
                continue
        if lbonly:
            if char == METACHAR_LINE_BREAK:
                exist_under_bar = True
                ret.append("O")
        else:
            ret.append("O")
    return ret


def get_score(data: typing.Dict[str, int]) -> typing.Dict[str, float]:
    ret: typing.Dict[str, float] = {}
    try:
        precision = data["TP"] / float(data["TP"] + data["FP"])
    except ZeroDivisionError:
        precision = float("nan")
    recall = data["TP"] / float(data["TP"] + data["FN"])
    ret["f1"] = 2 * precision * recall / (recall + precision)
    ret["precision"] = precision
    ret["recall"] = recall
    return ret


def evaluate(golds: typing.List[str], systems: typing.List[str], lbonly: bool) -> str:
    assert len(golds) == len(systems)
    golds_bo = []
    systems_bo = []
    for gold, system in zip(golds, systems):
        assert gold.replace(METACHAR_SENTENCE_BOUNDARY, "") == system.replace(
            METACHAR_SENTENCE_BOUNDARY, ""
        ), f"{gold}\n{system}"

        system_bo = get_bo(system, lbonly)
        systems_bo.append(system_bo)

        gold_bo = get_bo(gold, lbonly)
        golds_bo.append(gold_bo)
        assert len(gold_bo) == len(system_bo), (
            f"gold={gold} \nsystem={system}\n" f"N(gold)={len(gold_bo)} N(systems)={len(system_bo)}"
        )

    measure: typing.Dict[str, int] = performance_measure(golds_bo, systems_bo)
    score = get_score(measure)
    return f"{json.dumps(measure, sort_keys=True)}\n{json.dumps(score, sort_keys=True)}\n"


def trim(val: str) -> str:
    old: str = val
    new: str = val
    while True:
        new = RE_SBS_SPAN.sub(METACHAR_SENTENCE_BOUNDARY, RE_SB_WITH_BLANKS_SPAN.sub(r"\2\1", old))
        if old == new:
            break
        old = new
    return new


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=argparse.FileType("r"), required=True)
    oparser.add_argument("--gold", "-g", type=argparse.FileType("r"), required=False)
    oparser.add_argument("--output", "-o", type=argparse.FileType("w"), default="-")
    oparser.add_argument("--lb", action="store_true", help='Checks only Line-break marked with "\u2502"')
    oparser.add_argument("--trim", action="store_true")
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()
    with opts.output as outf:
        if opts.trim:
            for line in opts.input:
                outf.write(trim(line[:-1]))
                outf.write("\n")
        else:
            r = evaluate(
                [l1[:-1] for l1 in opts.gold.readlines()],
                [m[:-1] for m in opts.input.readlines()],
                opts.lb,
            )
            outf.write(r)


if __name__ == "__main__":
    main()
