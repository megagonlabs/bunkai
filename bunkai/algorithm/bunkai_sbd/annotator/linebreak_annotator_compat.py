#!/usr/bin/env python3
try:
    import numpy  # noqa: F401
    import torch  # noqa: F401
    import transformers  # noqa: F401
except ImportError:
    install_with_lb = False
else:
    install_with_lb = True

if install_with_lb:
    from bunkai.algorithm.bunkai_sbd.annotator.linebreak_annotator import LinebreakAnnotator  # type: ignore
else:
    # void class for compat
    class LinebreakAnnotator:
        def __init__(self, *, path_model):
            raise Exception("You need to install bunkai with pip install -U bunkai[lb]")
