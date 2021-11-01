#!/usr/bin/env python3
from typing import Dict, List, Type

from bunkai.algorithm.tsunoda_sbd.annotator.basic_annotator import BasicRule
from bunkai.algorithm.tsunoda_sbd.annotator.morph_annotator_janome import MorphAnnotatorJanome
from bunkai.base.annotation import Annotations, SpanAnnotation, TokenResult
from bunkai.base.annotator import Annotator


class ExceptionParticle(Annotator):
    def __init__(self, morph_annotator_class: Type[MorphAnnotatorJanome]):
        super().__init__(rule_name=self.__class__.__name__)
        self.morph_annotator_class = morph_annotator_class

    @staticmethod
    def is_exception_particle(
        original_text: str,
        start_index: int,
        end_index: int,
        index2token_obj: Dict[int, TokenResult],
    ) -> bool:
        """
        形態素解析の結果、基本分割文字列の後ろが助詞だった場合は 分割を行わない.

        例: 合宿免許? の若者さん達でしょうか / スタッフ? と話し込み .
        """
        __next_end_index = end_index
        if __next_end_index not in index2token_obj:
            return False
        else:
            token_obj = index2token_obj[__next_end_index]
            if token_obj.tuple_pos[0] == "助詞":
                return True
            else:
                return False

    def __generate(self, anns: List[SpanAnnotation]) -> Dict[int, TokenResult]:
        index2tokens = {}
        __start_index = 0
        __tokenizer_anns = [ann for ann in anns if ann.rule_name == self.morph_annotator_class.__name__]
        __processed = []
        for ann in __tokenizer_anns:
            t_obj = ann.args["token"]  # type: ignore
            if t_obj in __processed:
                continue
            __length = len(t_obj.word_surface)
            for __i in range(__start_index, __start_index + __length):
                index2tokens[__i] = t_obj
            __start_index += __length
            __processed.append(t_obj)
        else:
            return index2tokens

    def annotate(
        self,
        original_text: str,
        spans: Annotations,
    ) -> Annotations:
        index2token_obj = self.__generate(list(spans.get_annotation_layer(self.morph_annotator_class.__name__)))

        __return_span_ann = []
        for __s in spans.name2spans[BasicRule.__name__]:
            if self.is_exception_particle(
                original_text,
                __s.start_index,
                __s.end_index,
                index2token_obj=index2token_obj,
            ):
                continue
            else:
                __s.rule_name = self.rule_name
                __return_span_ann.append(__s)

        spans.add_annotation_layer(self.rule_name, __return_span_ann)
        return spans
