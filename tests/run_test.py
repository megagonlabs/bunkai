#!/usr/bin/env python3
import subprocess


def test():
    subprocess.run(
        ['python', '-u', '-m', 'unittest', 'discover']
    )
