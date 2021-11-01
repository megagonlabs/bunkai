#!/usr/bin/env python3
import ast
import typing


def get_method_names(tree_object):
    result: typing.Dict[int, typing.Tuple[str, int]] = {}
    searched_line_no = 0
    for node in ast.iter_child_nodes(tree_object):
        if isinstance(node, ast.FunctionDef):
            result[node.lineno] = (node.name, node.lineno)

        for child in ast.iter_child_nodes(node):
            get_method_names(child)

        if hasattr(node, "lineno"):
            if node.lineno > searched_line_no:
                searched_line_no = node.lineno
            else:
                t = result.get(node.lineno)
                if t is not None:
                    result[node.lineno] = (t[0], searched_line_no)

    return result


if __name__ == "__main__":
    import codecs
    import os
    import sys

    with codecs.open(sys.argv[1], "r", "utf-8") as f:
        try:
            source = f.read()
        except UnicodeDecodeError:
            raise Exception(sys.argv[1])

    tree = ast.parse(source, os.path.basename(sys.argv[1]))
    import re

    pattern = re.compile(r"split|divide|文分割")

    for line_no, v in get_method_names(tree).items():
        if len(pattern.findall(v[0])) > 0:
            raise Exception(f"method name violation {v[0]} at file-name = {sys.argv[1]}")
