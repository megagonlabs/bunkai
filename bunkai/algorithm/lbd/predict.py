#!/usr/bin/env python3

import argparse
import sys
import typing
from pathlib import Path

import numpy as np
import torch
from more_itertools import chunked
from transformers.models.auto.modeling_auto import AutoModelForTokenClassification

import bunkai.constant
from bunkai.algorithm.lbd.corpus import LABEL_OTHER, LABEL_SEP, annotation2spans
from bunkai.algorithm.lbd.custom_tokenizers import JanomeSubwordsTokenizer, JanomeTokenizer
from bunkai.algorithm.lbd.train import BunkaiConfig, MyDataset
from bunkai.base.annotation import Tokens
from bunkai.third.utils_ner import InputExample, get_labels

StringMorphemeInputType = typing.List[typing.List[str]]  # (batch-size * variable-length of sentence * tokens)


class Predictor(object):
    def __init__(self, modelpath: Path) -> None:
        """
        Use JanomeTokenizer by default if the input is Document(String).

        If the input is Morpheme(String), Tokenizers are not called.

        :param subword_tokenizer_type: pre_tokenize, janome, basic
        """
        self.model = AutoModelForTokenClassification.from_pretrained(str(modelpath))
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)

        self.labels = get_labels(str(modelpath.joinpath("labels.txt")))
        self.label_map: typing.Dict[int, str] = {i: label for i, label in enumerate(self.labels)}

        with modelpath.joinpath("bunkai.json").open() as bcf:
            self.bc = BunkaiConfig.from_json(bcf.read())
        # use janome tokenizer or tokenizer based on a vocab-file.
        self.path_tokenizer_model: str = str(Path(modelpath).joinpath("vocab.txt"))
        self.tokenizer = JanomeSubwordsTokenizer(self.path_tokenizer_model)

        # hotfix
        if self.model.base_model_prefix == "distilbert" and "token_type_ids" in self.tokenizer.model_input_names:
            self.tokenizer.model_input_names.remove("token_type_ids")

    def _split_long_text(
        self, tokens: typing.List[str]
    ) -> typing.Tuple[typing.List[typing.List[str]], typing.List[typing.List[int]]]:
        """
        Split documents(tokens) into sub-documents(tokens).

        This is because Bert has the maximum token-length of the input.
        """
        # tokenized_spans_list is a temporary stack which holds subword-token and underbar.
        # That is because underbar is replaced into UNK if underbar is put into a subword-tokeniser.
        tokenized_spans_list: typing.List[typing.List[str]] = []
        tmp_stack: typing.List[str] = []
        for __t in tokens:
            if __t == bunkai.constant.METACHAR_LINE_BREAK:
                if len(tmp_stack) > 0:
                    tokenized_spans_list.append(tmp_stack)
                tokenized_spans_list.append([bunkai.constant.METACHAR_LINE_BREAK])
                tmp_stack = []
            else:
                # sub-word tokenize
                tmp_stack.append(__t)
        if len(tmp_stack) > 0:
            tokenized_spans_list.append(tmp_stack)

        # run subword-tokeniser
        processed_tokens: typing.List[typing.List[str]] = [[]]
        processed_num_sws: typing.List[typing.List[int]] = [[]]
        current_count: int = 0
        tokenized_span: typing.List[str]
        for tokenized_span in tokenized_spans_list:
            for word in tokenized_span:
                subwords = self.tokenizer.tokenize(word)
                num_subwords = len(subwords)
                current_count += num_subwords
                if current_count >= self.bc.max_seq_length:
                    processed_tokens.append([])
                    processed_num_sws.append([])
                    current_count = num_subwords
                    assert current_count < self.bc.max_seq_length
                processed_tokens[-1].append(word)
                processed_num_sws[-1].append(num_subwords)
        return processed_tokens, processed_num_sws

    def predict(self, documents_morphemes: StringMorphemeInputType) -> typing.List[typing.Set[int]]:
        """
        Run prediction on incoming inputs. Inputs are 2 dims array with [[sentence]].

        :param spans_list: 2 dims list (batch-size * variable-length of sentence) or
        [['ラウンジ', 'も', '気軽', 'に', '利用', 'でき', '、', '申し分', 'ない', 'です', '。', '▁', '']].
        """
        examples = []

        # Note: gave up to separate this process in MyDataset because _split_long_text calls a tokenizer.
        num_subwords = []
        for d_id, spans in enumerate(documents_morphemes):
            sentences_within_length, _num_subwords = self._split_long_text(spans)
            num_subwords += _num_subwords
            for local_s_id, tokenized_spans in enumerate(sentences_within_length):
                examples.append(
                    InputExample(
                        guid=f"{d_id}-{local_s_id}",
                        words=tokenized_spans,
                        labels=[LABEL_OTHER] * len(tokenized_spans),
                        is_document_first=bool(local_s_id == 0),
                    )
                )
        ds = MyDataset(examples, self.labels, self.bc.max_seq_length, self.tokenizer, False)

        kwargs = {
            "input_ids": torch.tensor([f.input_ids for f in ds.features], device=self.device),
            "attention_mask": torch.tensor([f.attention_mask for f in ds.features], device=self.device),
        }
        if self.model.base_model_prefix == "bert":  # hotfix
            kwargs["token_type_ids"] = torch.tensor([f.token_type_ids for f in ds.features], device=self.device)

        predictions = self.model(**kwargs).logits.to("cpu").detach().numpy()

        assert isinstance(
            predictions, np.ndarray
        ), f"Unexpected error. A value type of a model prediction is {type(predictions)}. expect = numpy.ndarray"
        assert len(predictions.shape) == 3, (
            f"Unexpected error. A value tensor of a model prediction is {len(predictions.shape)} tensor. "
            f"expect = 3rd tensor."
        )

        out: typing.List[typing.Set[int]] = []
        word_idx_offset = 0
        for idx, (example, pred) in enumerate(zip(examples, predictions)):
            sw_idx = 0
            if example.is_document_first:
                word_idx_offset = 0  # reset
                out.append(set())
            else:
                word_idx_offset += len(examples[idx - 1].words)

            for word_idx, _ in enumerate(example.words):
                num_sw: int = num_subwords[idx][word_idx]
                while num_sw > 0:
                    sw_idx += 1
                    label_high_prob = int(np.argmax(pred[sw_idx]))
                    if self.label_map[label_high_prob] == LABEL_SEP:
                        out[-1].add(word_idx + word_idx_offset)
                    num_sw -= 1

        return out


def get_opts() -> argparse.Namespace:
    oparser = argparse.ArgumentParser()
    oparser.add_argument("--input", "-i", type=argparse.FileType("r"), required=False, default=sys.stdin)
    oparser.add_argument(
        "--output",
        "-o",
        type=argparse.FileType("w"),
        required=False,
        default=sys.stdout,
    )
    oparser.add_argument("--model", "-m", type=Path, required=True)
    oparser.add_argument("--batch", "-b", type=int, default=1, help="Number of documents to feed a batch")
    return oparser.parse_args()


def generate_initial_annotation_obj(
    input_stream: typing.Iterator[str],
) -> typing.Iterator[typing.List[str]]:
    tokenizer = JanomeTokenizer()
    for document in input_stream:
        # document: a text = document
        assert bunkai.constant.METACHAR_SENTENCE_BOUNDARY not in document
        document_spans: Tokens = annotation2spans(document[:-1])
        document_tokens: typing.List[str] = []
        for fragment in document_spans.spans:
            if bunkai.constant.METACHAR_LINE_BREAK in fragment:
                document_tokens.append(fragment)
            else:
                tokens = tokenizer.tokenize(fragment)
                document_tokens += tokens

        assert "".join(document_tokens) == "".join(document_spans.spans)
        yield document_tokens


def main() -> None:
    opts = get_opts()
    pdt = Predictor(opts.model)

    with opts.input as inf, opts.output as outf:
        for one_batch in chunked(generate_initial_annotation_obj(inf), n=opts.batch):
            for did, token_ids_seps in enumerate(pdt.predict(one_batch)):
                for tid, token in enumerate(one_batch[did]):
                    outf.write(token)
                    if tid in token_ids_seps:
                        outf.write(bunkai.constant.METACHAR_SENTENCE_BOUNDARY)
                else:
                    outf.write("\n")


if __name__ == "__main__":
    main()
