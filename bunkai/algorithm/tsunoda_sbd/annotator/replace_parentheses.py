#!/usr/bin/env python3
import re
from typing import Dict, List

from bunkai.algorithm.tsunoda_sbd.annotator import constant
from bunkai.base.annotation import SpanAnnotation
from bunkai.base.annotator import Annotations, Annotator


class ExceptionParentheses(Annotator):
    def __init__(self):
        super().__init__(rule_name=self.__class__.__name__)
        self.re_spans_parentheses1 = re.compile(constant.SPANS_PARENTHESES1_REGEXP)
        self.re_spans_parentheses2 = re.compile(constant.SPANS_PARENTHESES2_REGEXP)

    def replace_parentheses_no1(self, original_text: str, split_points: List[SpanAnnotation]) -> List[SpanAnnotation]:
        """
        括弧内に次の文字列があった場合は、括弧及び括弧内の文字列を一文とする.

        例:  ̃ (近日中には冷房に切り替わる予定です。) ̃ 1 時間飲み放題(カクテル各種! ! )はお勧め.
        """

        def unique_obj(input_list: List[SpanAnnotation]) -> List[SpanAnnotation]:
            # filter out same index
            filtered = []
            __added = []
            for s in input_list:
                if s.end_index not in __added:
                    filtered.append(s)
                __added.append(s.end_index)
            return filtered

        spans_parentheses = self.re_spans_parentheses1.finditer(original_text)
        filtered_split_point = []
        skip_end_index = []
        for parentheses_point in spans_parentheses:
            p_start_index = parentheses_point.regs[0][0]
            p_end_index = parentheses_point.regs[0][1]
            for split_candidate in split_points:
                __split_char = original_text[split_candidate.start_index : split_candidate.end_index]
                if p_start_index < split_candidate.start_index and split_candidate.end_index < p_end_index:
                    if __split_char in constant.CHARS_FOR_IGNORE_PARENTHESES1:
                        # 該当の区切り文字候補は破棄。代わりに()のインデックス情報
                        __new_parentheses_point = SpanAnnotation(
                            rule_name=self.rule_name,
                            start_index=p_end_index - 1,
                            end_index=p_end_index,
                            split_string_type="parentheses-sentence",
                            split_string_value=original_text[p_start_index:p_end_index],
                        )
                        filtered_split_point.append(__new_parentheses_point)
                        skip_end_index.append(split_candidate.end_index)
                    else:
                        pass
                else:
                    pass
            else:
                pass
        else:
            pass

        for s in split_points:
            if s.end_index not in skip_end_index:
                filtered_split_point.append(s)

        return unique_obj(filtered_split_point)

    # FIXME: Duplicated span bug
    def replace_parentheses_no2(self, original_text: str, split_points: List[SpanAnnotation]) -> List[SpanAnnotation]:
        """
        括弧内に、括弧の扱い(1)の文字列ではない基本分割文字列が現れた場合は、二回以上登場した際に限り分割点を付与する.

        要するに、括弧内で文境界付与を与えるということ.

        例: ̃(セルフドリンクサービスはすごく良かったです!種類も豊富。).
        """
        spans_parentheses = list(self.re_spans_parentheses2.finditer(original_text))
        filtered_split_point: List[SpanAnnotation] = []

        target_strings_positions: Dict[int, SpanAnnotation] = {}
        for split_candidate in split_points:
            __split_char = original_text[split_candidate.start_index : split_candidate.end_index]
            if __split_char in constant.CHARS_FOR_IGNORE_PARENTHESES2:
                target_strings_positions[split_candidate.end_index] = split_candidate

        # add split points between parentheses and frequency is more than 2 inside parentheses
        for parentheses_point in spans_parentheses:
            p_start_index = parentheses_point.regs[0][0]
            p_end_index = parentheses_point.regs[0][1]
            __split_char_in_parentheses = [
                (end_pos, reg_obj)
                for end_pos, reg_obj in target_strings_positions.items()
                if p_start_index < end_pos < p_end_index
            ]
            if len(__split_char_in_parentheses) >= 2:
                filtered_split_point += [t[1] for t in __split_char_in_parentheses]

        # add split points outside of parentheses
        t_span_parentheses = [
            (parentheses_point.regs[0][0], parentheses_point.regs[0][1]) for parentheses_point in spans_parentheses
        ]

        def is_outside_of_parentheses(t_s):
            if s_point.split_string_type == "parentheses-sentence":
                return True
            elif s_point.start_index <= t_s[0] and s_point.end_index <= t_s[0]:
                return True
            elif s_point.start_index >= t_s[1] and s_point.end_index >= t_s[1]:
                return True
            else:
                return False

        for s_point in split_points:
            _ = [is_outside_of_parentheses(t_s) for t_s in t_span_parentheses]
            if len(_) > 0 and all(_):
                filtered_split_point.append(s_point)

        return filtered_split_point

    def annotate(self, original_text: str, spans: Annotations) -> Annotations:
        __s_no1 = self.replace_parentheses_no1(original_text, spans.get_final_layer())
        if len(re.findall(r"\(.+\)", original_text)) > 0:
            __s_no2 = self.replace_parentheses_no2(original_text, __s_no1)
        else:
            __s_no2 = __s_no1

        spans.add_annotation_layer(self.rule_name, __s_no2)

        return spans
