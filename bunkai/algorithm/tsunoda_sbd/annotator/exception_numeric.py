#!/usr/bin/env python3
import re

from bunkai.base.annotation import Annotations
from bunkai.base.annotator import Annotator


class ExceptionNumeric(Annotator):
    def __init__(self):
        super().__init__(rule_name=self.__class__.__name__)

    @staticmethod
    def is_exception_numeric(original_text: str, start_index: int, end_index: int) -> bool:
        """
        .の前後が数値であった場合は分割を行わない.

        例: 和室3.5畳 / 1.5リットル以上のペットボトル.
        """
        if original_text[start_index:end_index] != "." and original_text[start_index:end_index] != "．":
            return False
        if re.match(r"\d", original_text[start_index - 1]) and re.match(r"\d", original_text[end_index]):
            return True
        return False

    def annotate(self, original_text: str, spans: Annotations) -> Annotations:
        __return_span_ann = []
        for __s in spans.get_final_layer():
            if self.is_exception_numeric(original_text, __s.start_index, __s.end_index):
                continue
            else:
                __s.rule_name = self.rule_name
                __return_span_ann.append(__s)

        spans.add_annotation_layer(self.rule_name, __return_span_ann)
        return spans
