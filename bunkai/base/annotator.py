#!/usr/bin/env python3
import typing
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Callable, Iterator, List, Optional

from bunkai.base.annotation import Annotations, SpanAnnotation


def func_filter_span(
    spans_wide: typing.List[SpanAnnotation], spans_narrow: typing.List[SpanAnnotation]
) -> typing.List[SpanAnnotation]:
    """Compare spans_wide and spans_narrow. If there is an overlap, use wider one."""
    __filtered = []
    for b_ann in spans_narrow:
        is_skip = False
        b_span = b_ann.get_spans()
        for f_ann in spans_wide:
            if b_span.within(f_ann.get_spans()):
                is_skip = True
            else:
                pass
        if is_skip is False:
            __filtered.append(b_ann)
    return __filtered


def func_filter_previous_rule_same_span(
    spans_current: typing.List[SpanAnnotation],
    spans_previous: typing.List[SpanAnnotation],
) -> typing.List[SpanAnnotation]:
    """If there are conflicting results, use the result of the previous rules."""
    spans_current_map = {(sp.start_index, sp.end_index): sp for sp in spans_current}
    spans_previous_map = {(sp.start_index, sp.end_index): sp for sp in spans_previous}
    common_key = list(set(spans_current_map.keys()) & set(spans_previous_map.keys()))
    filtered = []
    for span_key, sp in spans_current_map.items():
        if span_key in common_key:
            continue
        else:
            filtered.append(sp)
    return filtered + spans_previous


class RuleOrderException(Exception):
    """class if the order of rule is out-of-definition."""


class Annotator(metaclass=ABCMeta):
    def __init__(self, rule_name: str):
        self.rule_name = rule_name

    def add_forward_rule(
        self,
        annotation_this_layer: List[SpanAnnotation],
        spans: Annotations,
        func_filtering: Callable = func_filter_previous_rule_same_span,
    ) -> Annotations:
        filtered = func_filtering(annotation_this_layer, spans.get_final_layer())
        spans.add_annotation_layer(self.rule_name, filtered)
        return spans

    @abstractmethod
    def annotate(self, original_text: str, spans: Annotations) -> Annotations:
        raise NotImplementedError()


class AnnotationFilter(Annotator):
    @staticmethod
    def unify_span_annotations(
        span_annotations: List[SpanAnnotation],
    ) -> List[SpanAnnotation]:
        span_anns = {str(ann): ann for ann in span_annotations}
        return list(span_anns.values())


class AnnotatorPipeline(metaclass=ABCMeta):
    def __init__(self, pipeline: List[Annotator]):
        self.pipeline = pipeline
        self.check()

    @abstractmethod
    def check(self) -> bool:
        raise NotImplementedError()

    def __iter__(self):
        return iter(self.pipeline)


class SentenceBoundaryDisambiguator(metaclass=ABCMeta):
    def __init__(self, *, path_model: Optional[Path] = None):
        pass

    @abstractmethod
    def eos(self, text: str) -> Annotations:
        raise NotImplementedError()

    @abstractmethod
    def find_eos(self, text: str) -> List[int]:
        raise NotImplementedError()

    @abstractmethod
    def __call__(self, text: str) -> Iterator[str]:
        raise NotImplementedError()
