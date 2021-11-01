#!/usr/bin/env python3
import re

from bunkai.base.annotation import Annotations, SpanAnnotation
from bunkai.base.annotator import Annotator

RE_LBS = re.compile(r"[\n\s]*\n[\n\s]*")


class LinebreakForceAnnotator(Annotator):
    def __init__(self):
        super().__init__(rule_name=self.__class__.__name__)

    def annotate(self, original_text: str, spans: Annotations) -> Annotations:
        s2regs = {}
        for r_obj in RE_LBS.finditer(original_text):
            s: int = r_obj.regs[0][0]
            s2regs[s] = r_obj.regs[0]

        __return_span_ann = []

        def _add(ro):
            __return_span_ann.append(
                SpanAnnotation(
                    rule_name=self.rule_name,
                    start_index=s,
                    end_index=ro[1],
                    split_string_type="linebreak",
                    split_string_value=original_text[ro[0] : ro[1]],
                )
            )

        for __s in spans.get_final_layer():
            ro = s2regs.get(__s.end_index)
            if ro is None:
                __return_span_ann.append(__s)
            else:
                _add(ro)
                del s2regs[__s.end_index]

        for ro in s2regs.values():
            _add(ro)

        spans.add_annotation_layer(self.rule_name, __return_span_ann)
        return spans
