#!/usr/bin/env python3
import unittest
from collections import namedtuple

from bunkai.algorithm.bunkai_sbd.annotator.basic_annotator import BasicRule
from bunkai.algorithm.bunkai_sbd.annotator.constant import LAYER_NAME_FIRST
from bunkai.algorithm.bunkai_sbd.annotator.emoji_annotator import \
    EmojiAnnotator
from bunkai.algorithm.bunkai_sbd.annotator.emotion_expression_annotator import \
    EmotionExpressionAnnotator
from bunkai.algorithm.bunkai_sbd.annotator.facemark_detector import \
    FaceMarkDetector
from bunkai.algorithm.bunkai_sbd.annotator.indirect_quote_exception_annotator import \
    IndirectQuoteExceptionAnnotator
from bunkai.algorithm.bunkai_sbd.annotator.linebreak_annotator import \
    LinebreakAnnotator
from bunkai.algorithm.bunkai_sbd.annotator.morph_annotator import \
    MorphAnnotatorJanome
from bunkai.base.annotation import Annotations, SpanAnnotation

MorphResult = namedtuple('MorphResult', ('input_text', 'seq_linebreak_position'))


class TestMorphAnnotator(unittest.TestCase):
    def setUp(self) -> None:
        self.morph_annotator = MorphAnnotatorJanome()
        self.test_input = [
            MorphResult('この値段で、こんな夕飯いいの？\nって、くらいおいしかった！', [29])
        ]

    def init_tokenized_layer(self, text: str) -> Annotations:
        annotations = Annotations()
        annotations.add_annotation_layer(LAYER_NAME_FIRST, [SpanAnnotation(rule_name='first',
                                                                           start_index=len(text) - 1,
                                                                           end_index=len(text),
                                                                           split_string_type=None,
                                                                           split_string_value=None)])
        pipeline = [
            BasicRule(),
            FaceMarkDetector(),
            EmotionExpressionAnnotator(),
            EmojiAnnotator()
        ]
        for annotator in pipeline:
            annotator.annotate(text, annotations)
        self.morph_annotator.annotate(text, annotations)
        return annotations

    def test_if_linebreak_annotator_false(self):
        # LinebreakAnnotatorの予測が間違っていた場合のテストケース
        text = 'この値段で、こんな夕飯いいの？\nって、くらいおいしかった！'
        default_annotation = self.init_tokenized_layer(text)
        # LinebreakAnnotatorの疑似出力を作る
        pseudo_out_linebreak = [SpanAnnotation(
            rule_name=LinebreakAnnotator.__name__,
            start_index=15,
            end_index=16,
            split_string_type=None,
            split_string_value=None,
            args=None)] + list(default_annotation.get_annotation_layer('first'))
        default_annotation.add_annotation_layer(annotations=pseudo_out_linebreak,
                                                annotator_name=LinebreakAnnotator.__name__)
        indirect_exception = IndirectQuoteExceptionAnnotator()
        result_annotation = indirect_exception.annotate(original_text=text, spans=default_annotation)
        self.assertEqual(len(result_annotation.get_final_layer()), 1)

    def test_indirect_quote_exception_annotator(self):
        pass


if __name__ == '__main__':
    unittest.main()
