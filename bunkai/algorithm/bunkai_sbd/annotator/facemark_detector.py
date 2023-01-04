#!/usr/bin/env python3
import re
from pathlib import Path
from typing import List, Optional

from bunkai.algorithm.bunkai_sbd.annotator import constant
from bunkai.base.annotation import SpanAnnotation
from bunkai.base.annotator import Annotations, Annotator

RE_FACEMARK = re.compile(constant.FACE_EXPRESSION_REGEXP)


class FaceMarkDetector(Annotator):
    def __init__(self, *, path_model: Optional[Path] = None):
        super().__init__(FaceMarkDetector.__name__)

    @staticmethod
    def __find_facemark(text: str) -> List[SpanAnnotation]:
        __spans = []
        for match_obj in RE_FACEMARK.finditer(text):
            ann = SpanAnnotation(
                rule_name=FaceMarkDetector.__name__,
                start_index=match_obj.regs[0][0],
                end_index=match_obj.regs[0][1],
                split_string_type="facemark",
                split_string_value=text[match_obj.regs[0][0] : match_obj.regs[0][1]],
            )
            __spans.append(ann)
        return __spans

    def annotate(self, original_text: str, spans: Annotations) -> Annotations:
        span_ann = self.__find_facemark(original_text)
        spans = self.add_forward_rule(span_ann, spans)
        return spans
