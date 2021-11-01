#!/usr/bin/env python3
from pathlib import Path
from typing import Iterator, List, Optional

from bunkai.algorithm.bunkai_sbd.annotator import (
    BasicRule,
    DotExceptionAnnotator,
    EmojiAnnotator,
    EmotionExpressionAnnotator,
    FaceMarkDetector,
    IndirectQuoteExceptionAnnotator,
    LinebreakAnnotator,
    LinebreakForceAnnotator,
    MorphAnnotatorJanome,
    NumberExceptionAnnotator,
)
from bunkai.algorithm.bunkai_sbd.annotator.constant import LAYER_NAME_FIRST
from bunkai.base.annotation import Annotations, SpanAnnotation
from bunkai.base.annotator import AnnotatorPipeline, RuleOrderException, SentenceBoundaryDisambiguator


class BunkaiPipeline(AnnotatorPipeline):
    def check(self) -> bool:
        """
        Check following rule-order.

        1. MorphAnnotatorJanome must be before ExceptionParticle

        2. LinebreakFilter must be in the last position

        3. Facemark detector should be at first position

        """
        class_name2order = {process.rule_name: __i for __i, process in enumerate(self.pipeline)}
        if class_name2order[BasicRule.__name__] < class_name2order[FaceMarkDetector.__name__]:
            raise RuleOrderException(f"{FaceMarkDetector.__name__} should be at first position.")
        if class_name2order[BasicRule.__name__] < class_name2order[EmotionExpressionAnnotator.__name__]:
            raise RuleOrderException(f"{EmotionExpressionAnnotator.__name__} should be before {BasicRule.__name__}.")
        if class_name2order[MorphAnnotatorJanome.__name__] > class_name2order[IndirectQuoteExceptionAnnotator.__name__]:
            raise RuleOrderException(
                f"{MorphAnnotatorJanome.__name__}  must be" f" before {IndirectQuoteExceptionAnnotator.__name__}"
            )
        if LinebreakAnnotator.__name__ in class_name2order:
            if class_name2order[MorphAnnotatorJanome.__name__] > class_name2order[LinebreakAnnotator.__name__]:
                raise RuleOrderException(
                    f"{MorphAnnotatorJanome.__name__}  must be" f" before {LinebreakAnnotator.__name__}"
                )
            if (
                class_name2order[LinebreakAnnotator.__name__]
                > class_name2order[IndirectQuoteExceptionAnnotator.__name__]
            ):
                raise RuleOrderException(
                    f"{LinebreakAnnotator.__name__}  must be" f" before {IndirectQuoteExceptionAnnotator.__name__}"
                )
        return True


class BunkaiSentenceBoundaryDisambiguation(SentenceBoundaryDisambiguator):
    def __init__(self, *, path_model: Optional[Path] = None):
        morph_annotator = MorphAnnotatorJanome()

        _annotators = [
            FaceMarkDetector(),
            EmotionExpressionAnnotator(),
            EmojiAnnotator(),
            BasicRule(),
            morph_annotator,
            IndirectQuoteExceptionAnnotator(),
            DotExceptionAnnotator(),
            NumberExceptionAnnotator(),
        ]

        if path_model is None:
            _annotators.append(LinebreakForceAnnotator())
        else:
            _idxs = [i for i, ann in enumerate(_annotators) if ann.rule_name == MorphAnnotatorJanome.__name__]
            assert len(_idxs) > 0, f"{MorphAnnotatorJanome.__name__} does not exist in a pipeline"
            _annotators.insert(_idxs[0] + 1, LinebreakAnnotator(path_model=path_model))

        self.pipeline = BunkaiPipeline(_annotators)
        super().__init__()

    def eos(self, text: str) -> Annotations:
        annotations = Annotations()
        annotations.add_annotation_layer(
            LAYER_NAME_FIRST,
            [
                SpanAnnotation(
                    rule_name=LAYER_NAME_FIRST,
                    start_index=len(text) - 1,
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
