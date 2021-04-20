
# Algorithms

Bunkai has two algorithms: ``tsunoda`` and ``bunkai``.

## tsunoda

An implementation described in [角田孝昭, "顧客レビューテキスト解析に基づく文書作成支援に関する研究", 筑波大学博士論文 (2016)](http://hdl.handle.net/2241/00143820).

## bunkai

It exploits [following annotators](../bunkai/algorithm/bunkai_sbd/annotator).

- ``FaceMarkDetector``
    - detects a character span of face-marks. This is rule-based. The detected spans are excepted from SB candidates.
- ``EmotionExpressionAnnotator``
    - detects a character span of emotional expressions such as ``（笑）``. This is rule-based. The detected spans are excepted from SB candidates.
- ``BasicRule``
    - detects SB candidates based on rules.
- ``MorphAnnotatorJanome``
    - runs a morphological analyzer on the input text.
- ``EmojiAnnotator``
    - detects a character span of Emoji characters. This module is rule-based. With default rule, Emoji in ``Smileys & Emotion``, ``Symbols`` categories are SB candidates.  For getting to know Emoji categories, see [this page](https://emojipedia.org/categories/)
- ``IndirectQuoteExceptionAnnotator``
    - detects spans of indirect quotations that do not have explicit quotation marks ``「」``. SBs within indirect quotations are exceptional. This process is rule-based using morphological information.
- ``DotExpressionExceptionAnnotatorc``
    - detects SB ``.`` characters between numbers such as ``1.2畳``. The detected characters are SBs.
- ``NumberExceptionAnnotator``
    - detects SB ``.`` characters between idiomatic expressions such as ``おすすめ度No.1``. The detected characters are SBs.
- For line breaks
    - ``LinebreakForceAnnotator``  (When ``-m`` option is not given)
        - deetect SB for all line breaks
    - ``LinebreakExceptionAnnotator`` (When ``-m`` option is given)
        - classifies line breaks whether they are SB or not
