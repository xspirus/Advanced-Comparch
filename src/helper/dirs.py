#!/usr/bin/env python3

import os

__all__ = ["updir"]

def updir(root, dirs=1):
    path = root
    for _ in range(dirs):
        path = os.path.dirname(path)
    return path
