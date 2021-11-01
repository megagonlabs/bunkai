#!/usr/bin/env python3
import unittest
from collections import namedtuple

from bunkai.algorithm.bunkai_sbd.annotator.morph_annotator import MorphAnnotatorJanome

from .annotation_test_base import TestAnnotatorBase

MorphResult = namedtuple("MorphResult", ("input_text", "seq_newline_position"))


class TestMorphAnnotator(TestAnnotatorBase):
    def test_tokenize(self):
        test_input = [MorphResult("宿を予約しました♪!まだ2ヶ月も先だけど。早すぎかな(笑)楽しみです★\n" "2文書目の先頭行です。▁改行はU+2581で表現します。", [25])]
        morph_annotator = MorphAnnotatorJanome()
        for case_tuple in test_input:
            seq_tokens = list(morph_annotator.tokenizer.tokenize(case_tuple.input_text))
            for position_newline in case_tuple.seq_newline_position:
                target_morph = seq_tokens[position_newline].surface
                self.assertEqual(target_morph, "\n")


if __name__ == "__main__":
    unittest.main()
