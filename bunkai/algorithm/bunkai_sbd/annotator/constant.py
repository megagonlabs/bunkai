#!/usr/bin/env python3

import typing

PUNCTUATIONS: str = "。!?.！？．"
EMOTION_SYMBOLS: str = "…\u2605\u2606\u266a"
EMOTION_CHARACTERS: typing.List[str] = list("笑泣汗涙怒嬉爆驚喜悲謎恥焦苦照憂")
EMOTION_EXPRESSIONS: typing.List[str] = "笑い|わら|泣き|怒り|照れ".split("|")
FACE_SYMBOL_PREFIX_SUFFIX: str = "[!-/:-@[-`{-~！-／：-＠［-｀｛-～\u00A1-\u0FFF\u1000-\u2FFF\u4E00艸]"
ALPHABETS_REGEXP: str = "a-zA-Z0-9ａ-ｚＡ-Ｚ０-９"
FACE_SYMBOL1_REGEXP: str = (
    "[" + ALPHABETS_REGEXP + "!-/:-@[-`{-~！-／：-＠［-｀｛-～ａ-ｚＡ-Ｚ０-９\u00A1-\u0FFF\u1000-\u2FFF\u4E00艸]"
)
FACE_SYMBOL2_REGEXP: str = "[!-/:-@[-`{-~！-／：-＠［-｀｛-～\u00A1-\u0FFF\u1000-\u2FFF\u4E00艸]"
FACE_EXPRESSION_REGEXP: str = (
    FACE_SYMBOL_PREFIX_SUFFIX
    + r"*[（\(]"
    + FACE_SYMBOL1_REGEXP
    + "*"
    + FACE_SYMBOL2_REGEXP
    + "+"
    + FACE_SYMBOL1_REGEXP
    + "*"
    + r"[）\)]"
    + FACE_SYMBOL_PREFIX_SUFFIX
    + "*"
)


NUMBER_WORD_REGEXP: str = r"[nNｎＮ][oOｏＯ]"

LAYER_NAME_FIRST = "first"
