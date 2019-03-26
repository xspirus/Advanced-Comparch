#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd
import itertools as it
import subprocess as sp
from functools import partial
import time as dt
from multiprocessing import Pool
import argparse

from helper.dirs import updir


def parse_arguments():
    """Argument parser.

    Returns
    -------

    config: str
        Configuration to run.

    time: bool
        Whether to time results or not.
    """
    parser = argparse.ArgumentParser(
        prog="run", description="Run CSLab AdvComparch Exercise 1 Benchmarks."
    )
    parser.add_argument(
        "--time", help="time each benchmark", action="store_true"
    )
    args = parser.parse_args()
    return args.time


def preparation(root, benchmarks):
    """Prepare folders for execution.

    Parameters
    ----------

    root: str
        Root of project.

    benchmarks: list of str
        The benchmarks that we are going to run.

    Returns
    -------

    result_dir: str
        Results directory.
        This directory contains a subfolder for each of
        the simulations, as well as subsubfolders for each
        configuration.
    """
    results = os.path.join(root, "results", "ex1")
    os.makedirs(results, exist_ok=True)
    configs = os.path.join(root, "data", "ex1", "configs")
    configs = list(map(lambda x: x.split(".txt")[0], os.listdir(configs)))
    for benchmark in benchmarks:
        benchdir = os.path.join(results, benchmark)
        os.makedirs(benchdir, exist_ok=True)
        for config in configs:
            confdir = os.path.join(benchdir, config)
            os.makedirs(confdir, exist_ok=True)
    return results


def zip_benchmarks_cmds(benchmarks, cmds):
    """Zip benchmarks with cmds.

    Mainly used to zip raytrace as rtview.

    Parameters
    ----------

    benchmarks: list of str
        Benchmarks available.

    cmds: list of list of str
        Cmds of each benchmarks split by space.

    Returns
    -------

    benchmarks_cmds: list of tuples
        Benchmarks name along with its command.
    """
    ret = []
    for benchmark in benchmarks:
        found = False
        for cmd in cmds:
            if benchmark in cmd[0]:
                ret.append((benchmark, cmd))
                found = True
                break
        if not found:
            for cmd in cmds:
                if "rtview" in cmd[0]:
                    ret.append((benchmark, cmd))
    return ret


def configure_options(config):
    """Find output names as well as options of this config.

    Parameters
    ----------

    config: str
        10m

    Returns
    -------

    options: list of tuples
        Names (for saving) and Options that will be used during pin execution.
    """
    config_file = os.path.join(root, "data", "ex1", "configs", f"{config}.txt")
    configs = pd.read_csv(config_file)
    outputs = ["10m.txt"]

    options = []
    for _, config in configs.iterrows():
        config = map(
            lambda x: f"-{x[0]} {x[1]}".split(), config.to_dict().items()
        )
        config = list(it.chain(*config))
        options.append(config)
    return list(zip(outputs, options))


def run_one(option, main, results, cmd, cwd):
    """Function to run one configuration of one benchmark.

    Parameters
    ----------

    option: tuple of str, list
        Name and options of this configuration.

    main: list of str
        Main command.

    results: str
        Directory of results.

    cmd: str
        Command for this benchmark.

    cwd: str
        Working directory for subprocess.
    """
    output, options = option
    output = os.path.join(results, output)
    main.extend(["-o", output])
    main.extend(options)
    main.extend(["--"])
    main.extend(cmd)
    sp.run(main, stdout=sp.DEVNULL, stderr=sp.DEVNULL, cwd=cwd, env=os.environ)


def run(root, results, benchmarks, config, time):
    """Function to run all benchmarks.

    Parameters
    ----------

    root: str
        Root of project.

    results: str
        Results directory.

    benchmarks: list of str
        Benchmarks to run.

    config: str
        10m

    time: bool
        Time or not each benchmark.
    """
    pin = os.path.join(root, "pin-3.6", "pin")
    pintool = os.path.join(
        root, "CSLab", "ex1", "pintool", "obj-intel64", "simulator.so"
    )
    parsec = os.path.join(root, "parsec-3.0")
    parsec_workspace = os.path.join(parsec, "parsec_workspace")
    os.environ["LD_LIBRARY_PATH"] = os.path.join(
        parsec, "pkgs", "libs", "hooks", "inst", "amd64-linux.gcc-serial", "lib"
    )
    cmds = os.path.join(parsec_workspace, "cmds_simlarge.txt")
    with open(cmds, "r") as fp:
        cmds = list(map(lambda x: x.strip().split(), fp.readlines()))
    benchmarks = zip_benchmarks_cmds(benchmarks, cmds)
    options = configure_options(config)
    main = [pin, "-t", pintool]
    for benchmark, cmd in benchmarks:
        directory = os.path.join(results, benchmark, config)
        start = dt.time()
        with Pool() as pool:
            pool.map(
                partial(
                    run_one,
                    main=main,
                    results=directory,
                    cmd=cmd,
                    cwd=parsec_workspace,
                ),
                options,
            )
        delta = dt.time() - start
        if time:
            print(f"Benchmark {benchmark} finished in {delta:04f} seconds")


if __name__ == "__main__":
    time = parse_arguments()
    path = os.path.abspath(os.path.dirname(__file__))
    root = updir(path, 2)
    benchmarks = os.path.join(root, "data", "ex1", "benchmarks.txt")
    with open(benchmarks, "r") as fp:
        benchmarks = list(map(lambda x: x.strip(), fp.readlines()))
    results = preparation(root, benchmarks)
    run(root, results, benchmarks, "10m", time)
