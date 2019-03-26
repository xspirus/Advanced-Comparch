#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
from collections import defaultdict

# Types
from typing import Sequence

from helper.dirs import updir


plt.rc('text', usetex=True)
plt.rc('font', family='serif')


def parse_arguments() -> str:
    """Argument parser.

    Returns
    -------

    config: str
        Configuration to run.
    """
    parser = argparse.ArgumentParser(prog="plot", description="Plot results for all configs")
    parser.add_argument(
        "config",
        help="config to run",
        type=str,
        choices=["L1", "L2", "TLB", "Prefetch"],
    )
    args = parser.parse_args()
    return args.config


def find_stats(outputs: Sequence[str], config: str):
    """Function to find ipc and mpki.

    Parameters
    ----------

    outputs: iterable of str
        The files to open.

    config: str
        {L1, L2, TLB, Prefetch}.

    Returns
    -------

    dataframe: pandas DataFrame
        DataFrame containing IPC MPKI and x-axis labels.
    """
    # dictionary containing x-axis strings
    axis_labels = {
        "L1": "{0}K-{1}-{2}B",
        "L2": "{0}K-{1}-{2}B",
        "TLB": "{0}E-{1}-{2}B",
        "Prefetch": "{0}",
    }
    # string to find config
    if config == "Prefetch":
        data = "L2_prefetching"
    elif config == "TLB":
        data = f"Data {config}"
    else:
        data = f"{config}-Data Cache"
    # string to find misses
    if config == "Prefetch":
        misses = "L2-Total-Misses"
    else:
        misses = f"{config}-Total-Misses"
    # iterate files
    results = defaultdict(list)
    for output in outputs:
        with open(output, "r") as fp:
            lines = list(map(lambda x: x.strip(), fp.readlines()))
        # find total instructions
        total_instructions = next(filter(lambda x: x.startswith("Total Instructions"), lines))
        total_instructions = int(total_instructions.split(":")[1])
        # find ipc
        ipc = next(filter(lambda x: x.startswith("IPC"), lines))
        ipc = float(ipc.split(":")[1])
        # find mpki
        mpki = next(filter(lambda x: x.startswith(misses), lines))
        mpki = int(mpki.split(":")[1].split()[0])
        mpki = mpki / (total_instructions / 1000)
        # find x axis labels
        xaxis = next(filter(lambda x: x.startswith(data), lines))
        index = lines.index(xaxis)
        if config == "Prefetch":
            prefetch = int(xaxis.split()[3].split(")")[0])
            results["LABEL"].append(axis_labels[config].format(prefetch))
        else:
            size = int(lines[index + 1].split(":")[1])
            assoc = int(lines[index + 3].split(":")[1])
            block = int(lines[index + 2].split(":")[1])
            results["LABEL"].append(axis_labels[config].format(size, assoc, block))
        results["IPC"].append(ipc)
        results["MPKI"].append(mpki)
    return pd.DataFrame(results)


def plot_one(dataframe, savedir: str, config: str):
    """Plot one benchmark's results.

    Parameters
    ----------

    dataframe: pandas DataFrame
        Contains labels for x-axis, as well as IPC and MPKI.

    savedir: str
        Directory in which to save the results.

    config: str
        {L1, L2, TLB, Prefetch}.
    """
    labels = {
        "L1": "Cache Size-Associativity-Block Size",
        "L2": "Cache Size-Associativity-Block Size",
        "TLB": "Entries-Associativity-Page Size",
        "Prefetch": "Prefetched Blocks"
    }
    savefile = os.path.join(savedir, f"{config}.pdf")
    x_axis_labels = dataframe["LABEL"].tolist()
    values = dataframe[["IPC", "MPKI"]]
    ax = values.plot(marker="o", markersize=8, figsize=(19.2, 10.8), xlim=None)
    # fix margins
    ax.margins(0.05)
    ax.relim()
    ax.autoscale()
    # beautify
    plt.grid()
    plt.title(rf"\bfseries IPC vs MPKI for {config}", fontsize=20)
    plt.xlabel(rf"\bfseries {labels[config]}", fontsize=18)
    plt.xticks(np.arange(len(x_axis_labels)), x_axis_labels, fontsize=16, rotation=45)
    plt.yticks(fontsize=16)
    plt.legend(fontsize=16)
    plt.savefig(savefile, bbox_inches="tight")


def plot(root: str, results: str, plots: str, benchmarks: Sequence[str], config: str):
    """Function to plot results for specific configuration.

    Parameters
    ----------

    root: str
        Root of project.

    results: str
        Results folder.

    plots: str
        Folder where plots will be saved.

    benchmarks: iterable of str
        Benchmarks run.

    config: str
        {L1, L2, TLB, Prefetch}.
    """
    for benchmark in benchmarks:
        savedir = os.path.join(plots, benchmark)
        os.makedirs(savedir, exist_ok=True)
        directory = os.path.join(results, benchmark, config)
        outputs = sorted(os.listdir(directory))
        outputs = map(lambda x: os.path.join(directory, x), outputs)
        dataframe = find_stats(outputs, config)
        plot_one(dataframe, savedir, config)


if __name__ == "__main__":
    config = parse_arguments()
    path = os.path.abspath(os.path.dirname(__file__))
    root = updir(path, 2)
    benchmarks_file = os.path.join(root, "data", "ex1", "benchmarks.txt")
    with open(benchmarks_file, "r") as fp:
        benchmarks = list(map(lambda x: x.strip(), fp.readlines()))
    results = os.path.join(root, "results", "ex1")
    plots = os.path.join(root, "reports", "ex1", "plots")
    os.makedirs(plots, exist_ok=True)
    plot(root, results, plots, benchmarks, config)
