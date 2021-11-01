#!/usr/bin/env python3
import dataclasses
import itertools
from typing import Any, Dict, Iterator, List, Optional, Tuple

import spans
from dataclasses_json import DataClassJsonMixin


class TokenResult:
    def __init__(
        self,
        node_obj: Any,
        tuple_pos: Tuple[str, ...],
        word_stem: str,
        word_surface: str,
        is_feature=True,
        is_surface=False,
        misc_info=None,
    ):
        self.node_obj = node_obj
        self.word_stem = word_stem
        self.word_surface = word_surface
        self.is_surface = is_surface
        self.is_feature = is_feature
        self.misc_info = misc_info
        self.tuple_pos = tuple_pos

    def __str__(self):
        return self.word_surface


@dataclasses.dataclass
class SpanAnnotation:
    rule_name: Optional[str]
    start_index: int
    end_index: int
    split_string_type: Optional[str]
    split_string_value: Optional[str]
    args: Optional[Dict[str, Any]] = None

    def __str__(self):
        return f"{self.start_index}-{self.end_index}/{self.rule_name}/{self.split_string_value}"

    def __int__(self) -> int:
        return self.end_index

    def __spans(self) -> spans.intrange:
        return spans.intrange(self.start_index, self.end_index)

    def get_spans(self) -> spans.intrange:
        return self.__spans()

    def update_rule_name(self, new_rule_name: str) -> None:
        self.rule_name = new_rule_name


@dataclasses.dataclass
class Annotations:
    annotator_forward: Optional[str] = None
    name2spans: Dict[str, List[SpanAnnotation]] = dataclasses.field(default_factory=dict)
    name2order: Dict[str, int] = dataclasses.field(default_factory=dict)
    current_order: int = 0

    def add_annotation_layer(self, annotator_name: str, annotations: List[SpanAnnotation]) -> None:
        self.name2spans[annotator_name] = annotations
        self.name2order[annotator_name] = self.current_order
        self.annotator_forward = annotator_name
        self.current_order += 1

    def add_flatten_annotations(self, annotations: List[SpanAnnotation]):
        self.name2spans = {
            str(r): list(g_obj)
            for r, g_obj in itertools.groupby(
                sorted(annotations, key=lambda a: a.rule_name),  # type: ignore
                key=lambda a: a.rule_name,
            )
        }

    def flatten(self) -> Iterator[SpanAnnotation]:
        return itertools.chain.from_iterable(self.name2spans.values())

    def get_final_layer(self) -> List[SpanAnnotation]:
        if self.annotator_forward is None:
            return []
        else:
            return self.name2spans[self.annotator_forward]

    def get_annotation_layer(self, layer_name: str) -> Iterator[SpanAnnotation]:
        assert layer_name in list(self.name2spans.keys()), f"{layer_name} not in analysis layers."
        span_anns = {str(ann): ann for ann in itertools.chain.from_iterable(self.name2spans.values())}
        for ann in span_anns.values():
            if ann.rule_name is not None and ann.rule_name == layer_name:
                yield ann
        return

    def get_morph_analysis(self, name_annotation_layer: str = "MorphAnnotatorJanome") -> Iterator[TokenResult]:
        """Get Tokens analysis from Janome."""
        assert name_annotation_layer in self.name2spans, f"{name_annotation_layer} not in annotation layer."
        for span_ann in self.name2spans[name_annotation_layer]:
            if span_ann.rule_name == name_annotation_layer:
                ret = span_ann.args["token"]  # type: ignore
                assert isinstance(ret, TokenResult)
                yield ret
        return

    def available_layers(self) -> List[str]:
        return list(self.name2spans.keys())


@dataclasses.dataclass
class Tokens(DataClassJsonMixin):
    meta: Dict[str, Any] = dataclasses.field(default_factory=dict)
    spans: List[str] = dataclasses.field(default_factory=list)
    labels: List[str] = dataclasses.field(default_factory=list)

    def pretty(self, label2surface: Dict[str, str]) -> str:
        rets: List[str] = []
        for idx, span in enumerate(self.spans):
            rets.append(span)
            label = self.labels[idx]
            olabel = label2surface.get(label)
            if olabel:
                rets.append(olabel)
        return "".join(rets)
