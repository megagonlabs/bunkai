#!/usr/bin/env python3
import codecs
import collections
import sys
import typing


def main():
    line2fnames: typing.DefaultDict[str, typing.List[str]] = collections.defaultdict(list)
    for fname in sys.argv:
        with codecs.open(fname, 'r', 'utf-8') as inf:
            line = inf.readline()[:-1]
            line2fnames[line].append(fname)
    common_line = ''
    common_num = 0
    for line, fnames in line2fnames.items():
        if len(fnames) > common_num:
            common_num = len(fnames)
            common_line = line
    if len(line2fnames) != 1:
        print(f'Common ({common_num}): {common_line}')
        print('Others:')
        for line, fnames in line2fnames.items():
            if line != common_line:
                print(f'\t{line}: \t{fnames}')
        sys.exit(1)


if __name__ == '__main__':
    main()
