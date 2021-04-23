#!/usr/bin/env python3
import dataclasses
import typing
import unittest

from bunkai.algorithm.bunkai_sbd.annotator.morph_annotator import \
    MorphAnnotatorJanome
from bunkai.base.annotator import Annotations, Annotator, SpanAnnotation


@dataclasses.dataclass
class TestInstance(object):
    text: str
    n_sentence: int
    expected_rules: typing.Optional[typing.List[typing.Optional[str]]] = None


class TestAnnotatorBase(unittest.TestCase):
    def setUp(self) -> None:
        self.morph_annotator = MorphAnnotatorJanome()

    def init_tokenized_layer(self, text: str) -> Annotations:
        annotations = Annotations()
        annotations.add_annotation_layer('first', [SpanAnnotation(rule_name=None,
                                                                  start_index=0,
                                                                  end_index=len(
                                                                      text),
                                                                  split_string_type=None, split_string_value=None)])
        self.morph_annotator.annotate(text, annotations)
        return annotations

    @staticmethod
    def init_layer(text: str) -> Annotations:
        annotations = Annotations()
        annotations.add_annotation_layer('first', [SpanAnnotation(rule_name=None,
                                                                  start_index=0,
                                                                  end_index=len(
                                                                      text),
                                                                  split_string_type=None, split_string_value=None)])
        return annotations

    def is_check_test_instance(self,
                               annotator: Annotator,
                               test_cases: typing.List[TestInstance],
                               is_tokenize: bool = False):
        for test_case in test_cases:
            if is_tokenize:
                input_layer = self.init_tokenized_layer(test_case.text)
            else:
                input_layer = self.init_layer(test_case.text)
            annotations = annotator.annotate(original_text=test_case.text, spans=input_layer)
            span_annotations = annotations.get_final_layer()
            self.assertEqual(set([s.rule_name for s in span_annotations if s.rule_name is not None]),  # type: ignore
                             set(test_case.expected_rules),  # type: ignore
                             msg=f'text={test_case.text}, '  # type: ignore
                                 f'{set([s.rule_name for s in span_annotations])} '  # type: ignore
                                 f'!= {set(test_case.expected_rules)}')  # type: ignore

    def test_annotate(self):
        pass
