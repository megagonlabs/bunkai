# Bunkai

[![PyPI version](https://badge.fury.io/py/bunkai.svg)](https://badge.fury.io/py/bunkai)
[![Python Versions](https://img.shields.io/pypi/pyversions/bunkai.svg)](https://pypi.org/project/bunkai/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Downloads](https://pepy.tech/badge/bunkai/week)](https://pepy.tech/project/bunkai)

[![CI](https://github.com/megagonlabs/bunkai/actions/workflows/ci.yml/badge.svg)](https://github.com/megagonlabs/bunkai/actions/workflows/ci.yml)
[![Typos](https://github.com/megagonlabs/bunkai/actions/workflows/typos.yml/badge.svg)](https://github.com/megagonlabs/bunkai/actions/workflows/typos.yml)
[![CodeQL](https://github.com/megagonlabs/bunkai/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/megagonlabs/bunkai/actions/workflows/codeql-analysis.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/640b02fa0164c131da10/maintainability)](https://codeclimate.com/github/megagonlabs/bunkai/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/640b02fa0164c131da10/test_coverage)](https://codeclimate.com/github/megagonlabs/bunkai/test_coverage)
[![markdownlint](https://img.shields.io/badge/markdown-lint-lightgrey)](https://github.com/markdownlint/markdownlint)
[![jsonlint](https://img.shields.io/badge/json-lint-lightgrey)](https://github.com/dmeranda/demjson)
[![yamllint](https://img.shields.io/badge/yaml-lint-lightgrey)](https://github.com/adrienverge/yamllint)

Bunkai is a sentence boundary (SB) disambiguation tool for Japanese texts.  
    Bunkaiは日本語文境界判定器です．

## Quick Start

### Install

```console
$ pip install -U bunkai
```

### Disambiguation without Models

```console
$ echo -e '宿を予約しました♪!まだ2ヶ月も先だけど。早すぎかな(笑)楽しみです★\n2文書目の先頭行です。▁改行はU+2581で表現します。' \
    | bunkai
宿を予約しました♪!│まだ2ヶ月も先だけど。│早すぎかな(笑)│楽しみです★
2文書目の先頭行です。▁│改行はU+2581で表現します。
```

- Feed a document as one line by using ``▁`` (U+2581) for line breaks.  
    1行は1つの文書を表します．文書中の改行は ``▁`` (U+2581) で与えてください．
- The output shows sentence boundaries with ``│`` (U+2502).  
    出力では文境界は``│`` (U+2502) で表示されます．

### Disambiguation for Line Breaks with a Model

If you want to disambiguate sentence boundaries for line breaks, please add a ``--model`` option with the path to the model.  
    改行記号に対しても文境界判定を行いたい場合は，``--model``オプションを与える必要があります．

First, please install extras to use ``--model`` option.  
    ``--model``オプションを利用するために、まずextraパッケージをインストールしてください．

```console
$ pip install -U 'bunkai[lb]'
```

Second, please setup a model. It will take some time.  
    次にモデルをセットアップする必要があります．セットアップには少々時間がかかります．

```console
$ bunkai --model bunkai-model-directory --setup
```

Then, please designate the directory.  
    そしてモデルを指定して動かしてください．

```console
$ echo -e "文の途中で改行を▁入れる文章ってありますよね▁それも対象です。" | bunkai --model bunkai-model-directory
文の途中で改行を▁入れる文章ってありますよね▁│それも対象です。
```

### Morphological Analysis Result

You can get morphological analysis results with ``--ma`` option.  
``--ma``オプションを付与すると形態素解析結果が得られます．

```console
$ echo -e '形態素解析し▁ます。結果を 表示します！' | bunkai --ma
形態素	名詞,一般,*,*,*,*,形態素,ケイタイソ,ケイタイソ
解析	名詞,サ変接続,*,*,*,*,解析,カイセキ,カイセキ
し	動詞,自立,*,*,サ変・スル,連用形,する,シ,シ
▁
EOS
ます	助動詞,*,*,*,特殊・マス,基本形,ます,マス,マス
。	記号,句点,*,*,*,*,。,。,。
EOS
結果	名詞,副詞可能,*,*,*,*,結果,ケッカ,ケッカ
を	助詞,格助詞,一般,*,*,*,を,ヲ,ヲ
 	記号,空白,*,*,*,*, ,*,*
表示	名詞,サ変接続,*,*,*,*,表示,ヒョウジ,ヒョージ
し	動詞,自立,*,*,サ変・スル,連用形,する,シ,シ
ます	助動詞,*,*,*,特殊・マス,基本形,ます,マス,マス
！	記号,一般,*,*,*,*,！,！,！
EOS
```

### Python Library

You can also use Bunkai as Python library.  
  BunkaiはPythonライブラリとしても使えます．

```python
from bunkai import Bunkai
bunkai = Bunkai()
for sentence in bunkai("はい。このようにpythonライブラリとしても使えます！"):
    print(sentence)
```

For more information, see [examples](example).  
    ほかの例は[examples](example)をご覧ください．

## Documents

- [Documents](docs)

## References

- Yuta Hayashibe and Kensuke Mitsuzawa.
    Sentence Boundary Detection on Line Breaks in Japanese.
    Proceedings of The 6th Workshop on Noisy User-generated Text (W-NUT 2020), pp.71-75.
    November 2020.
    [[PDF]](https://www.aclweb.org/anthology/2020.wnut-1.10.pdf)
    [[bib]](https://www.aclweb.org/anthology/2020.wnut-1.10.bib)

## License

Apache License 2.0
