#!/usr/bin/env python3
import unittest

from bunkai.base_models.annotations import SpanAnnotation
from bunkai.tsunoda_sbd.annotator.basic_annotator import BasicRule


class TsukubaSplitter_BasicRule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # procedures before tests are started. This code block is executed only once
        pass

    @classmethod
    def tearDownClass(cls):
        # procedures after tests are finished. This code block is executed only once
        pass

    def setUp(self):
        # procedures before every tests are started. This code block is executed every time
        pass

    def tearDown(self):
        # procedures after every tests are finished. This code block is executed every time
        pass

    def test_okay(self):
        rule_obj = BasicRule(path_mecab_config='/opt/mecab/bin/')
        test_sentence_1_ok = "これ、テスト文なんですけど(笑)" \
                             "本当?にこんなテキストでいいのかな☆" \
                             "10秒で考えて書いたよ." \
                             "おすすめ度No.1の和室3.5畳はあります。おしまい♪(近日中には冷房に切り替わる予定です。いいですね(泣))"
        __input = SpanAnnotation(rule_name=None,
                                 start_index=0,
                                 end_index=len(test_sentence_1_ok),
                                 split_string_type=None,
                                 split_string_value=None)
        rule_obj.annotate(test_sentence_1_ok, [__input])


if __name__ == '__main__':
    unittest.main()
