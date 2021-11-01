#!/usr/bin/env python3

import typing
from pathlib import Path


def message(func: typing.Callable):
    def wrapper(*args, **kwargs):
        print(f"-- {func.__name__ } --")
        func(*args, **kwargs)
        print("-- END --")

    return wrapper


@message
def example_basic_usage(input_text: str, path_newline_model: typing.Optional[Path] = None):
    from bunkai.algorithm.bunkai_sbd.bunkai_sbd import BunkaiSentenceBoundaryDisambiguation

    bunkai = BunkaiSentenceBoundaryDisambiguation(path_model=path_newline_model)
    iter_sentences = bunkai(input_text)
    for sent in iter_sentences:
        assert isinstance(sent, str)
        print(sent)


@message
def example_basic_usage_with_alias(input_text: str, path_newline_model: typing.Optional[Path] = None):
    from bunkai import Bunkai

    bunkai = Bunkai()
    iter_sentences = bunkai(input_text)
    for sent in iter_sentences:
        assert isinstance(sent, str)
        print(sent)


@message
def example_eos_character_index(input_text: str, path_newline_model: typing.Optional[Path] = None):
    """How to get character index of end-of-sentence."""
    from bunkai.algorithm.bunkai_sbd.bunkai_sbd import BunkaiSentenceBoundaryDisambiguation

    bunkai = BunkaiSentenceBoundaryDisambiguation(path_model=path_newline_model)
    iter_sentences = bunkai.find_eos(input_text)
    sent_start_index: int = 0
    for eos_index in iter_sentences:
        print(f"sentence from:{sent_start_index} until:{eos_index} text={input_text[sent_start_index:eos_index]}")
        sent_start_index = eos_index


@message
def example_morphological_analysis(input_text: str, path_newline_model: typing.Optional[Path] = None):
    """How to get morphemes during processes."""
    from bunkai.algorithm.bunkai_sbd.bunkai_sbd import BunkaiSentenceBoundaryDisambiguation

    bunkai = BunkaiSentenceBoundaryDisambiguation(path_model=path_newline_model)
    # all analysis process is stored in Annotations object
    annotation_obj = bunkai.eos(input_text)
    tokens = annotation_obj.get_morph_analysis()
    for token in tokens:
        print(f"{token.word_surface},", end="")
    print(end="\n")


@message
def example_error_analysis_during_process(input_text: str, path_newline_model: typing.Optional[Path] = None):
    """How to get objects after each layer."""
    from bunkai.algorithm.bunkai_sbd.bunkai_sbd import BunkaiSentenceBoundaryDisambiguation

    bunkai = BunkaiSentenceBoundaryDisambiguation(path_model=path_newline_model)
    # all analysis process is stored in Annotations object
    annotation_obj = bunkai.eos(input_text)
    layers = annotation_obj.available_layers()
    print(f"available layer names {layers}")
    for l_name in layers:
        spans = annotation_obj.get_annotation_layer(l_name)
        print(l_name)
        for span_ann_obj in spans:
            print(
                f" ({span_ann_obj.start_index}, {span_ann_obj.end_index} {span_ann_obj.split_string_value}), ", end=""
            )
        print(end="\n")


if __name__ == "__main__":
    PATH_NEWLINE_MODEL = None
    input_text = "宿を予約しました♪!まだ2ヶ月も先だけど。早すぎかな(笑)楽しみです★"
    example_basic_usage(input_text, PATH_NEWLINE_MODEL)
    example_basic_usage_with_alias(input_text, PATH_NEWLINE_MODEL)
    example_eos_character_index(input_text, PATH_NEWLINE_MODEL)
    example_morphological_analysis(input_text, PATH_NEWLINE_MODEL)
    example_error_analysis_during_process(input_text, PATH_NEWLINE_MODEL)
