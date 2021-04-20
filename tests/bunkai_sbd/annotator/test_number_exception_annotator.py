#!/usr/bin/env python3
import unittest
from collections import namedtuple

from bunkai.algorithm.bunkai_sbd.annotator.number_exception_annotator import \
    NumberExceptionAnnotator

from .annotation_test_base import TestAnnotatorBase, TestInstance

NewlineTestCase = namedtuple('NewlineTestCase', ('text', 'start_index', 'end_index', 'ans'))


class TestNumberExceptionAnnotator(TestAnnotatorBase):
    def test_is_exception_no(self):
        annotator = NumberExceptionAnnotator()

        self.test_sentences = [
            NewlineTestCase('No.1の商品', 2, 3, True),
            NewlineTestCase('ROOM No.411を予約しました。', 7, 8, True)
        ]
        for test_obj in self.test_sentences:
            out_annotator = annotator.is_exception_no(test_obj.text, test_obj.start_index, test_obj.end_index)
            self.assertEqual(out_annotator, test_obj.ans)

    def test_annotate(self):
        test_cases = [
            TestInstance('No.1の商品', 1, expected_rules=[]),
            TestInstance('ROOM No.411を予約しました。', 1, expected_rules=[]),
        ]
        annotator = NumberExceptionAnnotator()
        self.is_check_test_instance(annotator=annotator, test_cases=test_cases)


if __name__ == '__main__':
    unittest.main()
