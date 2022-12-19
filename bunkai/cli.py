#!/usr/bin/env python3

import argparse
import sys
import tempfile
import typing
import zipfile
from pathlib import Path

import bunkai.constant
from bunkai import __version__
from bunkai.algorithm.bunkai_sbd.bunkai_sbd import BunkaiSentenceBoundaryDisambiguation
from bunkai.algorithm.tsunoda_sbd.tsunoda_sbd import TsunodaSentenceBoundaryDisambiguation

DEFAULT_ALGORITHM = "bunkai"
algorithm2class: typing.Dict[str, typing.Type] = {
    DEFAULT_ALGORITHM: BunkaiSentenceBoundaryDisambiguation,
    "tsunoda": TsunodaSentenceBoundaryDisambiguation,
}


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument(
        "--algorithm",
        "-a",
        default=DEFAULT_ALGORITHM,
        choices=sorted(list(algorithm2class.keys())),
    )
    oparser.add_argument(
        "--input",
        "-i",
        type=Path,
        default="/dev/stdin",
        required=False,
    )
    oparser.add_argument(
        "--output",
        "-o",
        type=Path,
        default="/dev/stdout",
        required=False,
    )
    oparser.add_argument(
        "--model",
        "-m",
        type=Path,
    )
    oparser.add_argument(
        "--setup",
        action="store_true",
        help="Setup a model file",
    )
    oparser.add_argument(
        "--ma",
        action="store_true",
        help="Print Morphological analyses result",
    )
    oparser.add_argument(
        "--version",
        "-v",
        action="store_true",
        help="Print version",
    )
    return oparser.parse_args()


def is_install_with_lb() -> bool:
    try:
        import numpy  # noqa: F401
        import torch  # noqa: F401
        import transformers  # noqa: F401
    except ImportError:
        return False
    else:
        return True


def run(
    annotator,
    _text: str,
    ma: bool = False,
) -> typing.Iterator[str]:
    assert "\n" not in _text
    assert bunkai.constant.METACHAR_SENTENCE_BOUNDARY not in _text

    text: str = _text.replace(
        bunkai.constant.METACHAR_LINE_BREAK,
        "\n",
    )

    if ma:
        annotation_obj = annotator.eos(text)
        tokens = annotation_obj.get_morph_analysis()
        end_indices = set([s_a.end_index for s_a in annotation_obj.get_final_layer()])

        position: int = 0
        for (
            idx,
            token,
        ) in enumerate(tokens):
            prev_position: int = position
            if token.node_obj is None or token.word_surface == "\n":
                yield bunkai.constant.METACHAR_LINE_BREAK
                position += 1
            else:
                yield f"{token.word_surface}\t"
                node = token.node_obj
                yield f"{node.part_of_speech},{node.infl_type},{node.infl_form}"
                yield f",{node.base_form},{node.reading},{node.phonetic}"
                position += len(token.word_surface)
            yield "\n"
            for p in range(
                prev_position,
                position,
            ):
                if p + 1 in end_indices:
                    yield "EOS\n"
    else:
        __annotator_result: typing.List[int] = annotator.find_eos(text)

        last: int = 0
        for (
            idx,
            split_point,
        ) in enumerate(__annotator_result):
            yield text[last:split_point].replace(
                "\n",
                bunkai.constant.METACHAR_LINE_BREAK,
            )
            if idx != len(__annotator_result) - 1:
                yield bunkai.constant.METACHAR_SENTENCE_BOUNDARY
            last = split_point
        yield "\n"


def setup(
    path_model: Path,
    path_in: typing.Optional[Path],
):
    # if bunkai installed without [lb] option, import of lbd.dist fails
    from bunkai.algorithm.lbd.dist import restore

    sys.stderr.write("It takes time to setup. Please be patient.\n")
    with tempfile.TemporaryDirectory() as temp_path:
        import requests

        if path_in is None:
            url: str = "https://github.com/megagonlabs/bunkai/releases/download/v1.1.1/bunkai-model-setup-20210426.zip"
            sys.stderr.write(f"Downloading from {url}\n")
            res = requests.get(url)
            assert res.status_code == 200
            path_in = Path(temp_path).joinpath("setup.zip")
            with path_in.open("wb") as fout:
                fout.write(res.content)

        sys.stderr.write("Extracting...\n")
        path_src = Path(temp_path).joinpath("src")
        path_src.mkdir(
            exist_ok=True,
            parents=True,
        )
        with zipfile.ZipFile(path_in) as zipf:
            zipf.extractall(path_src)

        sys.stderr.write("Writing...\n")
        files = [f for f in path_src.iterdir()]
        assert len(files) == 1
        restore(
            files[0],
            path_model,
        )
    sys.stderr.write("Done!\n")


def main() -> None:
    opts = get_opts()

    if opts.version:
        print(f"Bunkai {__version__}")
        return

    install_with_lb = is_install_with_lb()
    if opts.model is not None and not install_with_lb:
        raise ImportError(
            "To use model, you need numpy, transformers, and torch. "
            "It is recommended to install bunkai with `pip install bunkai[lb]`."
        ) from None

    if opts.setup:
        assert opts.model is not None, "--model should be given"
        pin = opts.input
        if opts.input == Path("/dev/stdin"):
            pin = None
        setup(
            opts.model,
            pin,
        )
        return

    cls = algorithm2class[opts.algorithm]
    annotator = cls(path_model=opts.model)
    warned: bool = False

    with opts.input.open() as inf, opts.output.open("w") as outf:
        for line in inf:
            ol: str = line[:-1]
            if bunkai.constant.METACHAR_SENTENCE_BOUNDARY in ol:
                ol = ol.replace(
                    bunkai.constant.METACHAR_SENTENCE_BOUNDARY,
                    "",
                )
                if not warned:
                    sys.stderr.write(
                        "\033[91m"
                        f"[Warning] All {bunkai.constant.METACHAR_SENTENCE_BOUNDARY} will be removed for input\n"
                        "\033[0m"
                    )
                    warned = True

            for op in run(
                annotator,
                ol,
                opts.ma,
            ):
                outf.write(op)


if __name__ == "__main__":
    main()
