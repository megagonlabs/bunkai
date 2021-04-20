#!/usr/bin/env python3
import dataclasses
import unittest

from bunkai.constant import METACHAR_LINE_BREAK, METACHAR_SENTENCE_BOUNDARY
from bunkai.experiment.evaluate import trim


@dataclasses.dataclass
class TestInstance(object):
    input: str
    output: str


class TestTrim(unittest.TestCase):
    def test_trim(self):
        SB = METACHAR_SENTENCE_BOUNDARY
        LB = METACHAR_LINE_BREAK
        test_cases = [
            TestInstance(f'yy {SB}zz', f'yy {SB}zz'),
            TestInstance(f'yy {LB}{SB}zz', f'yy {LB}{SB}zz'),
            TestInstance(f'yy {LB}{SB} zz', f'yy {LB} {SB}zz'),
            TestInstance(f'yy {LB} {SB} zz', f'yy {LB}  {SB}zz'),

            TestInstance(f'yy{SB} zz', f'yy {SB}zz'),
            TestInstance(f'yy{SB}  zz', f'yy  {SB}zz'),

            TestInstance('yy zz', 'yy zz'),
            TestInstance('yy  zz', 'yy  zz'),

            TestInstance(f'yy {LB}zz', f'yy {LB}zz'),
            TestInstance(f'yy {LB} zz', f'yy {LB} zz'),

            TestInstance(f'y{SB}{LB}{SB}zz', f'y{LB}{SB}zz'),
        ]
        for tc in test_cases:
            self.assertEqual(trim(tc.input), tc.output)


if __name__ == '__main__':
    unittest.main()
