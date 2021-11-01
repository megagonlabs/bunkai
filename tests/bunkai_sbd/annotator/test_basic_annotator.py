#!/usr/bin/env python3
import unittest

from bunkai.algorithm.bunkai_sbd.annotator.basic_annotator import BasicRule

from .annotation_test_base import TestAnnotatorBase, TestInstance


class TestBasicRule(TestAnnotatorBase):
    def test_annotate(self):
        test_cases = [
            TestInstance("１文目。２文目！３文目？", 3, expected_rules=[BasicRule.__name__]),
            TestInstance("１文目.２文目．３文目。", 3, expected_rules=[BasicRule.__name__]),
        ]
        annotator = BasicRule()
        self.is_check_test_instance(annotator=annotator, test_cases=test_cases)


if __name__ == "__main__":
    unittest.main()
