#!/usr/bin/env python3
import re

from bunkai.algorithm.tsunoda_sbd.annotator import constant
from bunkai.base.annotation import Annotations, SpanAnnotation
from bunkai.base.annotator import Annotator

RE_SENT_SPLIT = re.compile("[" + constant.PUNCTUATIONS + "]+|" + constant.SYMBOLS)


class BasicRule(Annotator):
    def __init__(self):
        super().__init__(rule_name=self.__class__.__name__)

    def annotate(self, original_text: str, spans: Annotations) -> Annotations:
        reg_points = RE_SENT_SPLIT.finditer(original_text)

        __return = [
            SpanAnnotation(
                rule_name=self.rule_name,
                start_index=r_obj.regs[0][0],
                end_index=r_obj.regs[0][1],
                split_string_type="regular",
                split_string_value=original_text[r_obj.regs[0][0] : r_obj.regs[0][1]],
            )
            for r_obj in reg_points
        ]
        spans.add_annotation_layer(self.rule_name, __return)
        return spans
