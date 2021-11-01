#!/usr/bin/env python3
import unittest
from collections import namedtuple

import bunkai.constant
from bunkai import cli as cli_module
from bunkai.algorithm.bunkai_sbd.bunkai_sbd import BunkaiSentenceBoundaryDisambiguation

NewlineTestCase = namedtuple("NewlineTestCase", ("text", "n_sentences", "return_value"))


class TestCli(unittest.TestCase):
    def setUp(self) -> None:
        self.seq_test_case = [
            NewlineTestCase("とても喜んでいました（＊́ω‘＊）♪ＵＳＪで遊んだよ。", 2, []),
            NewlineTestCase("お部屋ってありますか？うれしいです。もしなければ、どちらでも", 3, []),
            NewlineTestCase(
                "11時前に着きましたお部屋の準備ができているとの事で早くにチェックインでき足腰が悪いので大変あり難かったです、"
                "部屋も広く掃除も行き届いていました、"
                "お風呂も色々あり特に薬草風呂が良かった露天風呂はあまり開放感はありません街中なのでしかたがないです、",
                1,
                [],
            ),
            NewlineTestCase("(^ ^) (^　^) 先月泊まりましたが とてもよかったです", 1, []),
        ]

    def test_cli(self):
        model = BunkaiSentenceBoundaryDisambiguation(path_model=None)
        for test_case in self.seq_test_case:
            output = "".join(
                [o for o in cli_module.run(model, test_case.text.replace("\n", bunkai.constant.METACHAR_LINE_BREAK))]
            )
            outsents = output.split(bunkai.constant.METACHAR_SENTENCE_BOUNDARY)
            self.assertEqual(len(outsents), test_case.n_sentences, msg=f"false sentence split={output}")


if __name__ == "__main__":
    unittest.main()
