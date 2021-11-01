#!/usr/bin/env python3
import re

from bunkai.algorithm.bunkai_sbd.annotator import constant
from bunkai.base.annotation import Annotations
from bunkai.base.annotator import AnnotationFilter

RE_NUMBER_WORD = re.compile(constant.NUMBER_WORD_REGEXP)


class NumberExceptionAnnotator(AnnotationFilter):
    def __init__(self):
        super().__init__(rule_name=self.__class__.__name__)

    @staticmethod
    def is_exception_no(original_text: str, start_index: int, end_index: int) -> bool:
        """
        .の前にNoがあり、かつ後ろが数字で合った場合には分割を行わない.

        例: おすすめ度No.1 / ROOM No.411.
        """
        if original_text[start_index:end_index] != "." and original_text[start_index:end_index] != "．":
            return False

        if (
            RE_NUMBER_WORD.match(original_text[start_index - 2 : start_index])
            and end_index < len(original_text)
            and re.match(r"\d", original_text[end_index])
        ):
            return True
        return False

    def annotate(self, original_text: str, spans: Annotations) -> Annotations:
        __return_span_ann = []
        for __s in spans.get_final_layer():
            if self.is_exception_no(original_text, __s.start_index, __s.end_index):
                continue
            else:
                __return_span_ann.append(__s)
        spans.add_annotation_layer(self.rule_name, __return_span_ann)
        return spans
