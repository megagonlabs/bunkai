#!/usr/bin/env python3

import typing
from pathlib import Path

from bunkai.algorithm.bunkai_sbd.annotator.morph_annotator import MorphAnnotatorJanome
from bunkai.algorithm.lbd.predict import Predictor
from bunkai.base.annotation import SpanAnnotation
from bunkai.base.annotator import Annotations, Annotator
from bunkai.constant import METACHAR_LINE_BREAK


class LinebreakAnnotator(Annotator):
    def __init__(self, *, path_model: Path):
        super().__init__(LinebreakAnnotator.__name__)
        self.linebreak_detector = Predictor(modelpath=path_model)

    @staticmethod
    def generate_sentence_structure(
        annotation_object: Annotations, *, splitter: str = "\n", attribute_name: str = "MorphAnnotatorJanome"
    ) -> typing.List[str]:
        input_tokens: typing.List[str] = [
            span_obj.args["token"].word_surface
            for span_obj in annotation_object.get_annotation_layer(attribute_name)
            if span_obj.args is not None
        ]
        sentence_tokens: typing.List[str] = []
        __sentence: str
        for tokens in input_tokens:
            if tokens == splitter:
                sentence_tokens.append(METACHAR_LINE_BREAK)
            else:
                sentence_tokens.append(tokens)

        return sentence_tokens

    @staticmethod
    def merge_preceding_eos(text: str, spans: typing.List[SpanAnnotation]) -> typing.List[SpanAnnotation]:
        # TODO: Make two annotators?
        current_index: int = 0
        processed_spans = []
        sorted_spans = list(sorted(spans, key=lambda s: s.start_index))
        while True:
            if current_index + 1 >= len(sorted_spans):
                break
            span_ann = sorted_spans[current_index]
            if (
                span_ann.end_index == sorted_spans[current_index + 1].start_index
                and sorted_spans[current_index + 1].rule_name == LinebreakAnnotator.__name__
            ):
                processed_spans.append(
                    SpanAnnotation(
                        rule_name=LinebreakAnnotator.__name__,
                        start_index=span_ann.start_index,
                        end_index=sorted_spans[current_index + 1].end_index,
                        split_string_type="linebreak",
                        split_string_value=text[span_ann.start_index : sorted_spans[current_index + 1].end_index],
                    )
                )
                current_index += 2
            else:
                processed_spans.append(span_ann)
                current_index += 1
        return processed_spans

    def annotate(self, original_text: str, spans: Annotations) -> Annotations:
        """Tokenize済み結果をデータ加工する。Predictorが求める形式にする."""
        sub_texts = self.generate_sentence_structure(spans)
        # tokenizerを更新する。すでにTokenize済みの結果を利用する。
        # self.linebreak_detector.reset_tokenizer(word_tokenizer_type='pre_tokenize', sentence2tokens=sentence2tokens)
        __result = list(self.linebreak_detector.predict([sub_texts]))

        new_spans = spans.get_final_layer()
        morpheme_sequence = list(spans.get_annotation_layer(MorphAnnotatorJanome.__name__))
        if len(__result) > 0:
            # result: typing.List[TokenIndex] = __result[0]  # type: ignore
            for result in __result:
                for predicted_index in result:
                    char_index_start = morpheme_sequence[predicted_index].start_index
                    char_index_end = morpheme_sequence[predicted_index].end_index
                    ann = SpanAnnotation(
                        rule_name=LinebreakAnnotator.__name__,
                        start_index=char_index_start,
                        end_index=char_index_end,
                        split_string_type="linebreak",
                        split_string_value=original_text[char_index_start:char_index_end],
                    )
                    new_spans.append(ann)
            merged_spans = self.merge_preceding_eos(original_text, new_spans)
            spans.add_annotation_layer(self.rule_name, merged_spans)
        else:
            spans.add_annotation_layer(self.rule_name, new_spans)

        return spans
