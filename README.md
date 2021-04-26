# Bunkai

[![PyPI version](https://badge.fury.io/py/bunkai.svg)](https://badge.fury.io/py/bunkai)
[![Python Versions](https://img.shields.io/pypi/pyversions/bunkai.svg)](https://pypi.org/project/bunkai/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

[![CircleCI](https://circleci.com/gh/megagonlabs/bunkai.svg?style=svg&circle-token=c555b8070630dfe98f0406a3892fc228b2370951)](https://app.circleci.com/pipelines/github/megagonlabs/bunkai)
[![Maintainability](https://api.codeclimate.com/v1/badges/640b02fa0164c131da10/maintainability)](https://codeclimate.com/github/megagonlabs/bunkai/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/640b02fa0164c131da10/test_coverage)](https://codeclimate.com/github/megagonlabs/bunkai/test_coverage)
[![markdownlint](https://img.shields.io/badge/markdown-lint-lightgrey)](https://github.com/markdownlint/markdownlint)
[![jsonlint](https://img.shields.io/badge/json-lint-lightgrey)](https://github.com/dmeranda/demjson)
[![yamllint](https://img.shields.io/badge/yaml-lint-lightgrey)](https://github.com/adrienverge/yamllint)

Bunkai is a sentence boundary (SB) disambiguation tool for Japanese texts.

## Quick Start

```console
$ pip install bunkai
$ echo -e '宿を予約しました♪!まだ2ヶ月も先だけど。早すぎかな(笑)楽しみです★\n2文書目の先頭行です。▁改行はU+2581で表現します。' \
    | bunkai
宿を予約しました♪!│まだ2ヶ月も先だけど。│早すぎかな(笑)│楽しみです★
2文書目の先頭行です。▁│改行はU+2581で表現します。
```

Feed a document as one line by using ``▁`` (U+2581) for line breaks.
The output shows sentence boundaries with ``│`` (U+2502).

If you want to disambiguate  sentence boundaries for line breaks, please add a `--model` option with the path to the model.
First time, please setup a  model.

```console
$ bunkai --model bunkai-model-directory --setup
```

Then, please designate the directory.

```console
$ echo -e "文の途中で改行を▁入れる文章ってありますよね▁それも対象です。" | bunkai --model bunkai-model-directory
文の途中で改行を▁入れる文章ってありますよね▁│それも対象です。
```

For more information, see [examples](example) or [documents](docs).

## References

- Yuta Hayashibe and Kensuke Mitsuzawa.
    Sentence Boundary Detection on Line Breaks in Japanese.
    Proceedings of The 6th Workshop on Noisy User-generated Text (W-NUT 2020), pp.71-75.
    November 2020.
    [[PDF]](https://www.aclweb.org/anthology/2020.wnut-1.10.pdf)
    [[bib]](https://www.aclweb.org/anthology/2020.wnut-1.10.bib)

## License

Apache License 2.0
