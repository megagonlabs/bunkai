#!/usr/bin/env python3
import unittest
from collections import namedtuple
from pathlib import Path
from unittest.mock import MagicMock, patch

from bunkai.algorithm.bunkai_sbd.annotator import MorphAnnotatorJanome
from bunkai.algorithm.bunkai_sbd.annotator.linebreak_annotator import \
    LinebreakAnnotator
from bunkai.base.annotation import Annotations, SpanAnnotation

from .annotation_test_base import TestAnnotatorBase

LinebreakTestCase = namedtuple('LinebreakTestCase', ('text', 'char_positions', 'return_value'))


class TestLinebreakExceptionAnnotator(TestAnnotatorBase):
    def setUp(self) -> None:
        self.morph_annotator = MorphAnnotatorJanome()
        self.test_sentences = [
            LinebreakTestCase(
                'ペンションの内装もご自分達でリノベーションされたとの事でしたが、とても綺麗で色使いもお洒落☆\n'
                'お風呂も大きく、のんびり出来ました☆\n'
                'また朝ご飯のキッシュがとても美味しくて２人でペロリと頂いてしまいました♪',
                [(46, 47), (65, 66)],
                [[27, 38, ]]
            ),
            LinebreakTestCase('お部屋に露天風呂と足湯が付いていて、\n'
                              'とっても素敵でした。これからもまた旅行にいくときには、\nぜひ利用したいです。',
                              [], [[]])
        ]

    def init_tokenized_layer(self, text: str) -> Annotations:
        annotations = Annotations()
        annotations.add_annotation_layer('first', [SpanAnnotation(rule_name=None,
                                                                  start_index=0,
                                                                  end_index=len(
                                                                      text),
                                                                  split_string_type=None, split_string_value=None)])
        self.morph_annotator.annotate(text, annotations)
        return annotations

    def test_run(self):
        path_model = Path('')

        for test_case in self.test_sentences:
            predictor_mock = MagicMock()
            predictor_mock.return_value = test_case.return_value

            predictor_init = MagicMock()
            predictor_init.return_value = None

            with patch('bunkai.algorithm.lbd.predict.Predictor.__init__', predictor_init):
                with patch('bunkai.algorithm.lbd.predict.Predictor.predict', predictor_mock):
                    splitter_obj = LinebreakAnnotator(path_model=path_model)
                    tokenized_layer = self.init_tokenized_layer(test_case.text)
                    span_result = splitter_obj.annotate(test_case.text, tokenized_layer)
                    assert 'LinebreakAnnotator' in span_result.name2spans
                    results_exception_annotator = [a for a in span_result.get_annotation_layer('LinebreakAnnotator')
                                                   if a.rule_name == 'LinebreakAnnotator']
                    assert len(results_exception_annotator) == len(test_case.char_positions)
                    __ = set([(spans.start_index, spans.end_index) for spans in results_exception_annotator])
                    assert __ == set(test_case.char_positions)


if __name__ == '__main__':
    unittest.main()
