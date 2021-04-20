#!/usr/bin/env python3

import argparse
import sys
import typing

import bunkai.constant
from bunkai.algorithm.bunkai_sbd.bunkai_sbd import \
    BunkaiSentenceBoundaryDisambiguation
from bunkai.algorithm.tsunoda_sbd.tsunoda_sbd import \
    TsunodaSentenceBoundaryDisambiguation

DEFAULT_ALGORITHM = 'bunkai'
algorithm2class: typing.Dict[str, typing.Type] = {
    DEFAULT_ALGORITHM: BunkaiSentenceBoundaryDisambiguation,
    'tsunoda': TsunodaSentenceBoundaryDisambiguation,
}


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--algorithm", "-a", default=DEFAULT_ALGORITHM,
                         choices=sorted(list(algorithm2class.keys())))
    oparser.add_argument("--input", "-i", type=argparse.FileType("r"), default='-')
    oparser.add_argument("--output", "-o", type=argparse.FileType("w"), default='-')
    oparser.add_argument("--model", "-m")
    return oparser.parse_args()


def run(annotator, _text: str) -> typing.Iterator[str]:
    assert '\n' not in _text
    assert bunkai.constant.METACHAR_SENTENCE_BOUNDARY not in _text

    text: str = _text.replace(bunkai.constant.METACHAR_LINE_BREAK, '\n')
    __annotator_result: typing.List[int] = annotator.find_eos(text)
    if len(__annotator_result) == 0 or __annotator_result[-1] != len(text):
        __annotator_result.append(len(text))

    last: int = 0
    for idx, split_point in enumerate(__annotator_result):
        yield text[last:split_point].replace('\n', bunkai.constant.METACHAR_LINE_BREAK)
        if idx != len(__annotator_result) - 1:
            yield bunkai.constant.METACHAR_SENTENCE_BOUNDARY
        last = split_point


def main() -> None:
    opts = get_opts()
    cls = algorithm2class[opts.algorithm]
    annotator = cls(path_model=opts.model)
    warned: bool = False

    with opts.input as inf,\
            opts.output as outf:
        for line in inf:
            ol: str = line[:-1]
            if bunkai.constant.METACHAR_SENTENCE_BOUNDARY in ol:
                ol = ol.replace(bunkai.constant.METACHAR_SENTENCE_BOUNDARY, '')
                if not warned:
                    sys.stderr.write(
                        '\033[91m'
                        f'[Warning] All {bunkai.constant.METACHAR_SENTENCE_BOUNDARY} will be removed for input\n'
                        '\033[0m')
                    warned = True

            for ot in run(annotator, ol):
                outf.write(ot)
            outf.write('\n')


if __name__ == '__main__':
    main()
