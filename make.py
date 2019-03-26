#!/usr/bin/env python3

import os
import argparse
import subprocess as sp


def parse_arguments():
    """Parse arguments of this program.

    Returns
    -------

    exercise: str
        Name of exercise.
    """
    parser = argparse.ArgumentParser(prog="make", description="Makefile like helper")
    parser.add_argument("exercise", type=int, choices=[1, 2, 3, 4])
    args = parser.parse_args()
    return f"ex{args.exercise}"


def make(root, exercise):
    """Run makes for each exercise.

    Parameters
    ----------

    root: str
        Root of project.

    exercise: str
        Exercise to make.
    """
    if exercise == "ex1":
        cwd = os.path.join(root, "CSLab", exercise, "pintool")
        pin = os.path.join(root, "pin-3.6")
        cmd = f"make clean PIN_ROOT={pin}".split()
        sp.run(cmd, cwd=cwd)
        cmd = f"make PIN_ROOT={pin}".split()
        sp.run(cmd, cwd=cwd)


if __name__ == "__main__":
    exercise = parse_arguments()
    root = os.path.abspath(os.path.dirname(__file__))
    make(root, exercise)
