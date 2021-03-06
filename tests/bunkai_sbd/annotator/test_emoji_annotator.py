#!/usr/bin/env python3
import unittest
from collections import namedtuple

from bunkai.algorithm.bunkai_sbd.annotator.emoji_annotator import EmojiAnnotator
from bunkai.base.annotation import Annotations

from .annotation_test_base import TestAnnotatorBase, TestInstance

MorphResult = namedtuple("MorphResult", ("input_text", "seq_newline_position"))


class TestMorphAnnotator(TestAnnotatorBase):
    def setUp(self) -> None:
        self.test_input = [
            MorphResult("ใใผใ๐ค๐ค๐คใฉใใใใ", [6]),
            MorphResult("ใใผใซ๐บใฎใฟใใใ๏ธFrankfurtใฎ๐บใฏKrombacher", []),
            MorphResult("ใใใๆโฌ๏ธ", [5]),
            MorphResult("๏ผๆ็ฎ๐๏ผๆ็ฎ๐๏ผๆ็ฎ๐๏ผๆ็ฎ๐๐ใใใใ", [4, 8, 12, 17]),
        ]

    def test_emoji_detector(self):
        emoji_annotator = EmojiAnnotator()
        for test_tuple in self.test_input:
            ann = Annotations()
            result = emoji_annotator.annotate(test_tuple.input_text, spans=ann)
            self.assertEqual(set([s.end_index for s in result.get_final_layer()]), set(test_tuple.seq_newline_position))

    def test_annotate(self):
        test_input = [
            TestInstance("ใใผใ๐ค๐ค๐คใฉใใใใ", n_sentence=2, expected_rules=[EmojiAnnotator.__name__]),
            TestInstance("ใใผใซ๐บใฎใฟใใใ๏ธFrankfurtใฎ๐บใฏKrombacher", n_sentence=2, expected_rules=[]),
            TestInstance("ใใใๆโฌ๏ธ", n_sentence=1, expected_rules=[EmojiAnnotator.__name__]),
            TestInstance("๏ผๆ็ฎ๐๏ผๆ็ฎ๐๏ผๆ็ฎ๐๏ผๆ็ฎ๐๐ใใใใ", n_sentence=5, expected_rules=[EmojiAnnotator.__name__]),
        ]
        annotator = EmojiAnnotator()
        self.is_check_test_instance(annotator=annotator, test_cases=test_input)


if __name__ == "__main__":
    unittest.main()
