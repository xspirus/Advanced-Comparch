#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

# Types
from typing import Sequence

from helper.dirs import updir


plt.rc("text", usetex=True)
plt.rc("font", family="serif")


def find_stats(output: str) -> pd.core.frame.DataFrame:
    """Function to find stats for ipc and mpkis.

    Parameters
    ----------

    output: str
        File with results.

    Returns
    -------

    dataframe: pandas DataFrame
        DataFrame containing results (IPC, L1-MPKI, L2-MPKI, TLB-MPKI).
    """
    labels = {
        "IPC": "IPC",
        "L1": "L1-Total-Misses",
        "L2": "L2-Total-Misses",
        "TLB": "Tlb-Total-Misses",
    }
    stats = defaultdict(list)
    with open(output, "r") as fp:
        lines = list(map(lambda x: x.strip(), fp.readlines()))
    totals = list(filter(lambda x: x.startswith("Total Instructions"), lines))[
        :-1
    ]
    totals = list(map(lambda x: int(x.split(":")[1]), totals))
    stats["TOTAL"] = totals
    for label, start in labels.items():
        temp = list(filter(lambda x: x.startswith(start), lines))[:-1]
        stats[label] = list(map(lambda x: float(x.split()[1]), temp))
    for label, start in list(labels.items())[1:]:
        stats[label] = list(
            map(lambda x: x[0] / (x[1] / 1000), zip(stats[label], totals))
        )
    return pd.DataFrame(stats)


def plot_one(dataframe: pd.core.frame.DataFrame, savedir: str, config: str):
    """Plot one benchmark's results.

    Parameters
    ----------

    dataframe: pandas DataFrame
        Contains labels for x-axis, as well as IPC and MPKI.

    savedir: str
        Directory in which to save the results.

    config: str
        10m.
    """
    y_labels = {"IPC": "IPC", "L1": "MPKI", "L2": "MPKI", "TLB": "MPKI"}
    for label in y_labels:
        savefile = os.path.join(savedir, f"{label}.png")
        values = dataframe[["TOTAL", label]]
        fig = plt.figure(figsize=(19.2, 10.8))
        ax = plt.gca()
        ax = values.plot(
            ax=ax, x="TOTAL", y=label, color="red", legend=False
        )
        # beautify axes
        ax.margins(0.05)
        ax.relim()
        ax.autoscale()
        plt.grid(True)
        # titles etc.
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)
        plt.xlabel(r"\bfseries Instructions", fontsize=18)
        plt.ylabel(rf"\bfseries {y_labels[label]}", fontsize=18)
        plt.title(rf"\bfseries {label}", fontsize=20)
        plt.savefig(savefile, bbox_inches="tight")


def plot(
    root: str, results: str, plots: str, benchmarks: Sequence[str], config="10m"
):
    for benchmark in benchmarks:
        savedir = os.path.join(plots, benchmark, config)
        os.makedirs(savedir, exist_ok=True)
        directory = os.path.join(results, benchmark, config)
        output = sorted(os.listdir(directory))
        output = next(map(lambda x: os.path.join(directory, x), output))
        dataframe = find_stats(output)
        plot_one(dataframe, savedir, config)


if __name__ == "__main__":
    path = os.path.abspath(os.path.dirname(__file__))
    root = updir(path, 2)
    benchmarks_file = os.path.join(root, "data", "ex1", "benchmarks.txt")
    with open(benchmarks_file, "r") as fp:
        benchmarks = list(map(lambda x: x.strip(), fp.readlines()))
    results = os.path.join(root, "results", "ex1")
    plots = os.path.join(root, "reports", "ex1", "plots")
    os.makedirs(plots, exist_ok=True)
    plot(root, results, plots, benchmarks)
