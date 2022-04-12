try:
    import numpy
    import transformers
    import torch
except ImportError:
    install_with_lb = False
else:
    install_with_lb = True

if install_with_lb:
    from bunkai.algorithm.bunkai_sbd.annotator.linebreak_annotator import LinebreakAnnotator
else:
    # void class for compat
    class LinebreakAnnotator:
        pass
