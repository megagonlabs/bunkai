#!/usr/bin/env python3
import typing
from typing import Iterator, List

from bunkai.algorithm.tsunoda_sbd.annotator import (
    BasicRule,
    ExceptionNo,
    ExceptionNumeric,
    ExceptionParentheses,
    ExceptionParticle,
    MorphAnnotatorJanome,
)
from bunkai.base.annotation import Annotations, SpanAnnotation
from bunkai.base.annotator import AnnotatorPipeline, RuleOrderException, SentenceBoundaryDisambiguator


class TsunodaPipeline(AnnotatorPipeline):
    def check(self) -> bool:
        # MorphAnnotator must be before ExceptionParticle
        order_morph_annotator = 0
        order_exception_particle = 0
        for __i, a in enumerate(self.pipeline):
            if isinstance(a, MorphAnnotatorJanome):
                order_morph_annotator = __i
            elif isinstance(a, ExceptionParticle):
                order_exception_particle = __i

        if order_morph_annotator > order_exception_particle:
            raise RuleOrderException(
                f"MorphAnnotator at {order_morph_annotator} must be"
                f" before ExceptionParticle at {order_exception_particle}"
            )

        return True


class TsunodaSentenceBoundaryDisambiguation(SentenceBoundaryDisambiguator):
    def __init__(self, *, path_model: typing.Any = None):
        morph_annotator = MorphAnnotatorJanome()  # type: ignore
        particle_annotator = ExceptionParticle(MorphAnnotatorJanome)

        self.pipeline = TsunodaPipeline(
            [
                BasicRule(),
                morph_annotator,
                particle_annotator,
                ExceptionNumeric(),
                ExceptionNo(),
                ExceptionParentheses(),
            ]
        )
        super().__init__()

    def eos(self, text: str) -> Annotations:
        annotations = Annotations()
        annotations.add_annotation_layer(
            "first",
            [
                SpanAnnotation(
                    rule_name=None,
                    start_index=0,
                    end_index=len(text),
                    split_string_type=None,
                    split_string_value=None,
                )
            ],
        )
        for rule_obj in self.pipeline:
            rule_obj.annotate(text, annotations)
        return annotations

    def find_eos(self, text: str) -> List[int]:
        annotations = self.eos(text)
        end_index = list(sorted(list(set([s_a.end_index for s_a in annotations.get_final_layer()]))))
        if len(end_index) == 0 or end_index[-1] != len(text):
            end_index.append(len(text))
        return end_index

    def __call__(self, text: str) -> Iterator[str]:
        annotations = self.eos(text)
        end_index = sorted(list(set([s_a.end_index for s_a in annotations.get_final_layer()])))
        __start_index = 0
        __end_index = 0
        for e_i in end_index:
            part_sentences = text[__start_index:e_i]
            __start_index = e_i
            __end_index = e_i
            yield part_sentences

        if __end_index < len(text):
            part_sentences = text[__end_index:]
            yield part_sentences
