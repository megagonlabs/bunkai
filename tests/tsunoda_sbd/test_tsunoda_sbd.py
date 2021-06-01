#!/usr/bin/env python3
import unittest

from bunkai.algorithm.tsunoda_sbd.tsunoda_sbd import \
    TsunodaSentenceBoundaryDisambiguation
from bunkai.base.annotation import Annotations


class TestTsukubaSplitter(unittest.TestCase):
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
        splitter_obj = TsunodaSentenceBoundaryDisambiguation()

        test_sentence_1_ok = "これ、テスト文なんですけど(笑)" \
                             "本当?にこんなテキストでいいのかな☆" \
                             "10秒で考えて書いたよ." \
                             "(セルフドリンクサービスはすごく良かったです!種類も豊富。)" \
                             "おすすめ度No.1の和室3.5畳はあります。" \
                             "おしまい♪" \
                             "(近日中には冷房に切り替わる予定です。いいですね(泣))"
        self.assertTrue(isinstance(splitter_obj.eos(
            test_sentence_1_ok), Annotations))
        self.assertEqual(len(splitter_obj.eos(
            test_sentence_1_ok).get_final_layer()), 7)
        self.assertEqual(len(splitter_obj.find_eos(test_sentence_1_ok)), 7)
        self.assertEqual(
            len(list(splitter_obj(test_sentence_1_ok))), 7)


if __name__ == '__main__':
    unittest.main()
