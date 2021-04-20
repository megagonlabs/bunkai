#!/usr/bin/env python3
import unittest

from bunkai.algorithm.bunkai_sbd.annotator.emotion_expression_annotator import \
    EmotionExpressionAnnotator

from .annotation_test_base import TestAnnotatorBase, TestInstance


class TestEmotionExpressionAnnotator(TestAnnotatorBase):
    def test_annotate(self):
        test_cases = [
            TestInstance('１文目（笑）２文目（汗）３文目（泣）', 3, expected_rules=[EmotionExpressionAnnotator.__name__]),
            TestInstance('１文目☆２文目★３文目。', 3, expected_rules=[EmotionExpressionAnnotator.__name__]),
        ]
        annotator = EmotionExpressionAnnotator()
        self.is_check_test_instance(annotator=annotator, test_cases=test_cases)


if __name__ == '__main__':
    unittest.main()
