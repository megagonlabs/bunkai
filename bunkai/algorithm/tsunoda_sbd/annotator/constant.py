#!/usr/bin/env python3

import typing

# \u2605: ★
# \u2606: ☆
# \u266a: ♪
PUNCTUATIONS: str = "。!?.！？．\u2605\u2606\u266a\\*＊※"
SYMBOLS: str = r"[（(\(]笑[）\))]|[（(\(]泣[）\))]|[（(\(]涙[）\))]"

SPANS_PARENTHESES1_REGEXP: str = r"\((?!涙|笑|泣).+?(?<!涙|笑|泣)\)"
SPANS_PARENTHESES2_REGEXP: str = r"\((?!涙|笑|泣).+?\)"
CHARS_FOR_IGNORE_PARENTHESES1: typing.Set[str] = {
    "。",
    ".",
    "．",
    "(笑)",
    "(泣)",
    "(涙)",
    "（笑）",
    "（泣）",
    "（涙）",
}
CHARS_FOR_IGNORE_PARENTHESES2: typing.Set[str] = {
    "!",
    "！",
    "?",
    "？",
    "\u2605",
    "\u2606",
    "\u266a",
    "*",
    "＊",
    "※",
}

NUMBER_WORD_REGEXP: str = r"[nNｎＮ][oOｏＯ]"
