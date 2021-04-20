#!/usr/bin/env python3
import unittest
from collections import namedtuple

from bunkai.algorithm.bunkai_sbd.annotator.dot_exception_annotator import \
    DotExceptionAnnotator

from .annotation_test_base import TestAnnotatorBase, TestInstance

NewlineTestCase = namedtuple('NewlineTestCase', ('text', 'start_index', 'ans'))


class TestDotExceptionAnnotator(TestAnnotatorBase):
    def test_is_exception_numeric(self):
        annotator = DotExceptionAnnotator()

        self.test_sentences = [
            NewlineTestCase('和室3.5畳', 3, True),
            NewlineTestCase('1.5リットル以上のペットボトル', 1, True),
            NewlineTestCase('四.五畳以上の大きさ', 1, True),
            NewlineTestCase('四五畳以上の大きさ', 1, False),
            NewlineTestCase('15メートル以上の大きさ', 1, False),
        ]
        for test_obj in self.test_sentences:
            out_annotator = annotator.is_exception_numeric(test_obj.text, test_obj.start_index)
            self.assertEqual(out_annotator, test_obj.ans)

    def test_annotate(self):
        annotator = DotExceptionAnnotator()
        test_sentences = [
            TestInstance('和室3.5畳', 1, expected_rules=[]),
            TestInstance('1.5リットル以上のペットボトル', 1, expected_rules=[]),
            TestInstance('四.五畳以上の大きさ', 1, expected_rules=[]),
            TestInstance('四五畳以上の大きさ', 1, expected_rules=[]),
            TestInstance('15メートル以上の大きさ', 1, expected_rules=[]),
        ]
        self.is_check_test_instance(annotator=annotator, test_cases=test_sentences)


if __name__ == '__main__':
    unittest.main()
