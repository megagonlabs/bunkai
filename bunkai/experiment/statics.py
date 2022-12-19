#!/usr/bin/env python3
import argparse
import collections
import dataclasses
import json
import typing
from pathlib import Path

import tqdm
from dataclasses_json import DataClassJsonMixin

import bunkai.constant
from bunkai.algorithm.lbd.corpus import LABEL_NSEP, LABEL_OTHER, LABEL_SEP, annotation2spans


@dataclasses.dataclass
class Statics(DataClassJsonMixin):
    name: str = ""
    num_file: int = 0
    line_break: int = 0
    line_break_without_sb: int = 0
    sentence: int = 0
    sentence_include_line_break: int = 0
    sentence_include_line_break_without_sb: int = 0

    def add(self, st):
        self.num_file += 1
        for f in dataclasses.fields(st):
            self.__setattr__(f.name, self.__getattribute__(f.name) + st.__getattribute__(f.name))


def count(path: Path, outf: typing.IO, show: bool = False) -> Statics:
    st = Statics()
    with path.open() as inf:
        for doc in inf:
            text = doc[:-1]
            st.sentence += text.count(bunkai.constant.METACHAR_SENTENCE_BOUNDARY)
            tokens = annotation2spans(text)
            if len(tokens.labels) == 0:
                continue
            if tokens.labels[-1] != LABEL_OTHER:
                del tokens.spans[-1]
                del tokens.labels[-1]
            cnt: int = 0
            line_break_without_sb: int = 0
            for label in tokens.labels:
                if label == LABEL_SEP:
                    cnt += 1
                elif label == LABEL_NSEP:
                    cnt += 1
                    line_break_without_sb += 1
            if cnt > 0:
                st.sentence_include_line_break += 1
            st.line_break += cnt

            st.line_break_without_sb += line_break_without_sb
            if line_break_without_sb > 0:
                st.sentence_include_line_break_without_sb += 1
                if show:
                    outf.write(f"{path}\t{tokens}\n")
    return st


def count_char(path: Path) -> typing.Iterator[str]:
    with path.open() as inf:
        for doc in inf:
            text = doc[:-1]
            tokens = annotation2spans(text)
            if len(tokens.labels) == 0:
                continue
            if tokens.labels[-1] != LABEL_OTHER:
                del tokens.spans[-1]
                del tokens.labels[-1]
            for tid, label in enumerate(tokens.labels):
                if tid < len(tokens.labels) - 1 and label == LABEL_OTHER:
                    yield tokens.spans[tid][-1]


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=Path, required=True)
    oparser.add_argument("--output", "-o", type=argparse.FileType("w"), default="-")
    oparser.add_argument("--show", action="store_true")
    oparser.add_argument("--char", action="store_true")
    return oparser.parse_args()


def main() -> None:
    opts = get_opts()

    targets: typing.List[typing.Tuple[str, Path]] = [("__", opts.input)]
    if opts.input.is_dir():
        targets = [(fi.name[:2], fi) for fi in opts.input.iterdir()]

    if opts.char:
        genre2chars: typing.Dict[str, typing.DefaultDict[str, int]] = {}
        genre2chars["ALL"] = collections.defaultdict(int)
        for genre, fpath in tqdm.tqdm(targets, leave=False):
            chars: typing.Optional[typing.DefaultDict[str, int]] = genre2chars.get(genre)
            if chars is None:
                chars = collections.defaultdict(int)
                genre2chars[genre] = chars
            for mychar in count_char(fpath):
                chars[mychar] += 1
                genre2chars["ALL"][mychar] += 1
        with opts.output as outf:
            for genre, chars in sorted(genre2chars.items()):
                outf.write(f"{genre}\t")
                outf.write(json.dumps(chars, ensure_ascii=False, sort_keys=True))
                outf.write("\n")
        return

    st_all = Statics(name="ALL")
    st_detail: typing.DefaultDict[str, Statics] = collections.defaultdict(Statics)
    with opts.output as outf:
        for genre, fpath in tqdm.tqdm(targets, leave=False):
            st = count(fpath, outf, opts.show)
            st_all.add(st)
            st_detail[genre].name = genre
            st_detail[genre].add(st)

        if not opts.show:
            if len(targets) != 1:
                for genre, st in sorted(st_detail.items()):
                    outf.write(f"{st.to_json()}\n")
            outf.write(f"{st_all.to_json()}\n")


if __name__ == "__main__":
    main()
