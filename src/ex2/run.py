#!/usr/bin/env python3

import os
import pandas as pd
import itertools as it
import subprocess as sp
from functools import partial
import time as dt
from multiprocessing import Pool
import argparse
from pprint import pprint

from typing import Sequence, Tuple

from helper.dirs import updir


def parse_arguments() -> bool:
    """Argument parser.
    
    Returns
    -------

    time: bool
        Whether to time results or not.
    """
    parser = argparse.ArgumentParser(
        prog="run", description="Run CSLab AdvComparch Exercise 2 Benchmarks"
    )
    parser.add_argument(
        "--time", help="time each benchmark", action="store_true"
    )
    args = parser.parse_args()
    return args.time


def preparation(root: str, benchmarks: Sequence[str]):
    """Prepare folders for execution.
    
    Parameters
    ----------

    root: str
        Root of project.

    benchmarks: iterable of str
        The benchmarks that we are going to run.

    Returns
    -------

    result_dir: str
        Results directory.
        This directory contains a subfolder for each of
        the simulations.
    """
    results = os.path.join(root, "results", "ex2")
    os.makedirs(results, exist_ok=True)
    for benchmark in benchmarks:
        if "." in benchmark:
            benchmark = benchmark.split(".")[1]
        benchdir = os.path.join(results, benchmark)
        os.makedirs(benchdir, exist_ok=True)
    return results


def commands(
    root: str, benchmarks: Sequence[str]
) -> Tuple[
    Sequence[str], Sequence[Sequence[str]], Sequence[str], Sequence[str]
]:
    """Get commands for each of the benchmarks.
    
    Parameters
    ----------

    root: str
        Root of project.

    benchmarks: iterable of str
        The benchmarks that we are going to run.

    Returns
    -------

    cwds: iterable of path-like
        The working directory for each benchmark.

    cmds: iterable of str
        The commands to be run.

    stdouts: iterable of path-like
        Standard output files for each benchmark.

    stderrs: iterable of path-like
        Standard error files for each benchmark.
    """
    inputs = os.path.join(root, "CSLab", "ex2", "spec_execs_train_inputs")
    cwds = []
    cmds = []
    stdouts = []
    stderrs = []
    for benchmark in benchmarks:
        cwd = os.path.join(inputs, benchmark)
        cwds.append(cwd)
        with open(os.path.join(cwd, "speccmds.cmd"), "r") as fp:
            cmd = fp.read().strip()
        stdout = cmd.split()[1]
        stderr = cmd.split()[3]
        cmd = cmd.split()[4:]
        cmds.append(cmd)
        stdouts.append(stdout)
        stderrs.append(stderr)
    return cwds, cmds, stdouts, stderrs


def run_one(config: Tuple, main: Sequence[str], time: bool):
    """Function to run one benchmark.
    
    Parameters
    ----------

    config: tuple
        Contains resultdir, benchmark, cwd, cmd, stdout, stderr

    main: iterable of str
        Main command to be executed.

    time: bool
        Time or not.
    """
    result, benchmark, cwd, cmd, stdout, stderr = config
    stdout = os.path.join(cwd, stdout)
    stderr = os.path.join(cwd, stderr)
    if "." in benchmark:
        benchmark = benchmark.split(".")[1]
    output = os.path.join(result, benchmark, f"{benchmark}.out")
    main.extend(["-o", output, "--"])
    main.extend(cmd)
    print(f"Executing benchmark {benchmark} with command:")
    print(f"  {' '.join(main)} 1> {stdout} 2> {stderr}")
    print(f"  in directory {cwd}")
    start = dt.time()
    with open(stdout, "w") as out:
        with open(stderr, "w") as err:
            sp.run(main, stdout=out, stderr=err, cwd=cwd)
    delta = dt.time() - start
    if time:
        print(f"Benchmark {benchmark} finished in {delta:04f} seconds")


def run(
    root: str,
    results: str,
    benchmarks: Sequence[str],
    configs: Sequence[Tuple],
    time: bool,
):
    """Function to run all benchmarks.
    
    Parameters
    ----------

    root: str
        Root of project.

    results: str
        Results directory.

    benchmarks: iterable of str
        Benchmarks to run.

    configs: iterable of tuples
        The necessary options for each benchmark (cwd, cmd, stdout, stderr).

    time: bool
        Time or not each benchmark.
    """
    pin = os.path.join(root, "pin-3.6", "pin")
    pintool = os.path.join(
        root, "CSLab", "ex2", "pintool", "obj-intel64", "cslab_branch.so"
    )
    main = [pin, "-t", pintool]
    configs = list(zip([results] * len(configs), benchmarks, *zip(*configs)))
    with Pool() as pool:
        pool.map(partial(run_one, main=main, time=time), configs)


if __name__ == "__main__":
    time = parse_arguments()
    path = os.path.abspath(os.path.dirname(__file__))
    root = updir(path, 2)
    benchmarks = os.path.join(root, "data", "ex2", "benchmarks.txt")
    with open(benchmarks, "r") as fp:
        benchmarks = list(map(lambda x: x.strip(), fp.readlines()))
    results = preparation(root, benchmarks)
    cmds = list(zip(*commands(root, benchmarks)))
    run(root, results, benchmarks, cmds, time)
