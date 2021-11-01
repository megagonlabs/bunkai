#!/usr/bin/env python3

import argparse
import random
import re
import sys
import typing
from pathlib import Path

from bunkai.algorithm.lbd.custom_tokenizers import JanomeTokenizer
from bunkai.base.annotation import Tokens
from bunkai.constant import METACHAR_LINE_BREAK, METACHAR_SENTENCE_BOUNDARY

REGEXP_LB_SPAN: str = (
    f"[\\s{METACHAR_SENTENCE_BOUNDARY}{METACHAR_LINE_BREAK}]*"
    + f"{METACHAR_LINE_BREAK}[\\s{METACHAR_LINE_BREAK}{METACHAR_SENTENCE_BOUNDARY}]*"
)
RE_LB_SPAN = re.compile(REGEXP_LB_SPAN)

LABEL_OTHER: str = "O"
LABEL_SEP: str = "LB_SEP"
LABEL_NSEP: str = "LB_NS"
LABELS: typing.List[str] = [LABEL_OTHER, LABEL_SEP, LABEL_NSEP]


def annotation2spans(sentence: str) -> Tokens:
    """
    Cut a sentence into list of sentence.

    Cation: Return value is Tokens, but this is not actual token. Set of text-segments.
    """
    prev: int = 0
    tokens = Tokens()
    for match in RE_LB_SPAN.finditer(sentence):
        myspan = sentence[prev : match.start()].replace(METACHAR_SENTENCE_BOUNDARY, "")
        if len(myspan) > 0:
            tokens.spans.append(myspan)
            tokens.labels.append(LABEL_OTHER)

        myspan = match.group()
        prev = match.end()
        tokens.spans.append(myspan.replace(METACHAR_SENTENCE_BOUNDARY, ""))
        if METACHAR_SENTENCE_BOUNDARY in myspan:
            tokens.labels.append(LABEL_SEP)
        else:
            tokens.labels.append(LABEL_NSEP)

    lastspan = sentence[prev:]
    if len(lastspan) != 0:
        tokens.spans.append(lastspan.replace(METACHAR_SENTENCE_BOUNDARY, ""))
        tokens.labels.append(LABEL_OTHER)

    assert sentence.replace(METACHAR_SENTENCE_BOUNDARY, "") == "".join(tokens.spans)
    return tokens


def _fix_tokens(mytxt: str, ts: typing.List[str]) -> typing.List[str]:
    # restore blanks erased by the tokeniser
    ret: typing.List[str] = []
    index: int = 0
    prev: int = 0
    for _token in ts:
        index += mytxt[index:].index(_token)
        if index != prev:
            ret.append(mytxt[prev:index])
        ret.append(_token)
        index += len(_token)
        prev = index
    lasttk = mytxt[index:]
    if len(lasttk) > 0:
        ret.append(lasttk)
    return ret


def spans2tokens(tokenizer: JanomeTokenizer, tokens: Tokens) -> Tokens:
    assert len(tokens.spans) == len(tokens.labels)
    new_tokens = Tokens()
    for mytxt, label in zip(tokens.spans, tokens.labels):
        if label == LABEL_OTHER:
            ts = tokenizer.tokenize(mytxt)
            ts = _fix_tokens(mytxt, ts)
            new_tokens.spans += ts
            new_tokens.labels += [LABEL_OTHER] * len(ts)
        else:  # Line break
            new_tokens.spans.append(mytxt)
            new_tokens.labels.append(label)

    return new_tokens


def convert(
    inpath: typing.IO,
    tokenizer: JanomeTokenizer,
    remove_trailing_lb: bool = True,
) -> typing.Iterator[Tokens]:
    with inpath as inf:
        for lid, line in enumerate(inf):
            sentence: str = line[:-1]
            if METACHAR_LINE_BREAK not in sentence:
                continue

            tokens = annotation2spans(sentence)
            if remove_trailing_lb and tokens.labels[-1] != LABEL_OTHER:
                tokens.spans = tokens.spans[:-1]
                tokens.labels = tokens.labels[:-1]
            if len(tokens.labels) == 1:
                continue
            new_tokens = spans2tokens(tokenizer, tokens)
            new_tokens.meta["lid"] = lid
            assert len(new_tokens.labels) == len(new_tokens.spans)
            assert sentence.replace(METACHAR_SENTENCE_BOUNDARY, "").startswith("".join(tokens.spans))
            yield new_tokens


def corpus_separate(
    lines: typing.List[str], ratio_train: float, ratio_dev: float
) -> typing.Dict[str, typing.List[str]]:
    rets: typing.Dict[str, typing.List[str]] = {}

    index_train = int(len(lines) * ratio_train)
    seq_train_set = lines[:index_train]
    seq_dev = seq_train_set[: int(len(seq_train_set) * ratio_dev)]
    seq_train = seq_train_set[int(len(seq_train_set) * ratio_dev) :]
    seq_test = lines[index_train:]

    rets["train"] = seq_train
    rets["test"] = seq_test
    rets["dev"] = seq_dev
    return rets


def pseudo_linebreak(text: str, rnd: random.Random, *, ratio_lb: float = 0.5) -> str:
    rets = []
    text = re.sub(r"。+", METACHAR_LINE_BREAK + METACHAR_SENTENCE_BOUNDARY, text)
    for char in text:
        if char == "、" and rnd.random() < ratio_lb:
            rets.append(METACHAR_LINE_BREAK)
        else:
            rets.append(char)
    return "".join(rets)


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=argparse.FileType("r"), default=sys.stdin)
    oparser.add_argument("--output", "-o", type=Path, required=True)
    oparser.add_argument("--split", action="store_true")
    oparser.add_argument("--pseudo", action="store_true")
    oparser.add_argument("--train", type=float, default=0.8)
    oparser.add_argument("--dev", type=float, default=0.0)
    oparser.add_argument("--seed", type=int, default=12345)
    oparser.add_argument("--base", default="cl-tohoku/bert-base-japanese-whole-word-masking")
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()

    if opts.split:
        lines = opts.input.readlines()
        random.Random(opts.seed).shuffle(lines)
        name2lines = corpus_separate(lines, ratio_train=opts.train, ratio_dev=opts.dev)
        opts.output.mkdir(exist_ok=True, parents=True)

        ppmap = {LABEL_SEP: METACHAR_SENTENCE_BOUNDARY}
        for name, lines in name2lines.items():
            opath = opts.output.joinpath(f"{name}.jsonl")
            otxtpath = opts.output.joinpath(f"{name}.txt")
            with opath.open("w") as f, otxtpath.open("w") as tf:
                for line in lines:
                    f.write(line)
                    ts = Tokens.from_json(line)
                    tf.write(f"{ts.pretty(ppmap)}\n")
    elif opts.pseudo:
        rnd = random.Random(opts.seed)
        with opts.output.open("w") as outf:
            for line in opts.input:
                line = line[:-1].replace(METACHAR_SENTENCE_BOUNDARY, "").replace(METACHAR_LINE_BREAK, "")
                line2 = pseudo_linebreak(line, rnd)
                outf.write(f"{line2}\n")
    else:
        opts.output.parent.mkdir(exist_ok=True, parents=True)
        tokenizer = JanomeTokenizer(normalize_text=False)
        with opts.output.open("w") as f:
            for tokens in convert(inpath=opts.input, tokenizer=tokenizer):
                f.write(f"{tokens.to_json(ensure_ascii=False, sort_keys=True)}\n")


if __name__ == "__main__":
    main()
