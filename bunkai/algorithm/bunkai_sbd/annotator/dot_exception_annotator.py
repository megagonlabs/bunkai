#!/usr/bin/env python3
import re

from bunkai.base.annotation import Annotations
from bunkai.base.annotator import AnnotationFilter

NumericExpression = re.compile(r"[〇一二三四五六七八九十百千万億兆京\d]+")
MailaddressCharacter = re.compile(r"[a-zA-Z0-9]")


class DotExceptionAnnotator(AnnotationFilter):
    def __init__(self):
        super().__init__(rule_name=self.__class__.__name__)

    @staticmethod
    def is_exception_numeric(original_text: str, index: int) -> bool:
        """
        Ignore dot between numbers.

        Eg: 和室3.5畳 / 1.5リットル以上のペットボトル.
        """
        if index <= 0:
            return False
        if index + 1 >= len(original_text):
            return False
        if original_text[index] != "．" and original_text[index] != ".":
            return False
        if not NumericExpression.match(original_text[index - 1]):
            return False
        if not NumericExpression.match(original_text[index + 1]):
            return False
        return True

    @staticmethod
    def is_exception_mailaddress(original_text: str, index: int) -> bool:
        if index <= 0:
            return False
        if index + 1 >= len(original_text):
            return False
        if original_text[index] != "．" and original_text[index] != ".":
            return False
        if not MailaddressCharacter.match(original_text[index - 1]):
            return False
        if not MailaddressCharacter.match(original_text[index + 1]):
            return False
        return True

    def annotate(self, original_text: str, spans: Annotations) -> Annotations:
        __return_span_ann = []
        for __s in spans.get_final_layer():
            if self.is_exception_numeric(original_text, __s.start_index):
                continue
            elif self.is_exception_mailaddress(original_text, __s.start_index):
                continue
            __return_span_ann.append(__s)

        spans.add_annotation_layer(self.rule_name, __return_span_ann)
        return spans
