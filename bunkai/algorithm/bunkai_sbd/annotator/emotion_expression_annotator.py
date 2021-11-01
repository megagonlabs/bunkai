#!/usr/bin/env python3
import re

from bunkai.algorithm.bunkai_sbd.annotator import constant
from bunkai.base.annotation import Annotations, SpanAnnotation
from bunkai.base.annotator import Annotator

PARENT_EMOTION = "|".join(constant.EMOTION_CHARACTERS + constant.EMOTION_EXPRESSIONS)
RE_PARENT_EMOTION = re.compile(
    r"[（\(](" + PARENT_EMOTION + r")[\)）]" + "|" + f"[{constant.EMOTION_SYMBOLS}]+[{constant.PUNCTUATIONS}]?"
)


class EmotionExpressionAnnotator(Annotator):
    def __init__(self):
        super().__init__(rule_name=self.__class__.__name__)

    def annotate(self, original_text: str, spans: Annotations) -> Annotations:
        reg_points = RE_PARENT_EMOTION.finditer(original_text)

        __return = [
            SpanAnnotation(
                rule_name=self.rule_name,
                start_index=r_obj.regs[0][0],
                end_index=r_obj.regs[0][1],
                split_string_type=EmotionExpressionAnnotator.__name__,
                split_string_value=original_text[r_obj.regs[0][0] : r_obj.regs[0][1]],
            )
            for r_obj in reg_points
        ]
        spans = self.add_forward_rule(__return, spans)
        return spans
