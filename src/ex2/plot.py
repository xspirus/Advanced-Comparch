#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
from collections import defaultdict
from pprint import pprint

# Types
from typing import Sequence, Dict

from helper.dirs import updir


np.random.seed(123)

_colors = []


_options = {
    "predictors": 14,
    "filetype": "png",
}


def parse_arguments():
    """Argument parser.
    
    Used to parse certain options and save them to
    global dictionary of options.
    """
    parser = argparse.ArgumentParser(
        prog="plot", description="Plot results"
    )
    parser.add_argument(
        "predictors",
        nargs="?",
        help="number of predictors",
        type=int,
        default=14,
    )
    parser.add_argument(
        "--filetype",
        nargs="?",
        help="save type",
        type=str,
        choices=["pdf", "png"],
        default="png",
    )
    args = parser.parse_args()
    _options.update(vars(args))
    return


def fix_name(benchmark: str):
    """Remove dot from benchmark name.
    
    Parameters
    ----------

    benchmark: str

    Returns
    -------

    benchmark: str
    """
    if "." in benchmark:
        benchmark = benchmark.split(".")[1]
    return benchmark


def make_colors():
    """Create random colors."""
    def random_hex():
        """Create random hex number."""
        return round(np.random.uniform(0, 1), 2)
    for _ in range(_options.get("predictors")):
        _colors.append((random_hex(), random_hex(), random_hex()))


def find_stats(output: str) -> Dict:
    """Function to find mpki for benchmark's predictors.
    
    Parameters
    ----------

    output: str
        The file to find stats from.

    Returns
    -------

    stats: dict of str, float
        The stats found for each predictor.
    """
    stats: Dict = {}
    with open(output, "r") as fp:
        line = fp.readline()

        while line:
            tokens = line.split()
            if line.startswith("Total Instructions"):
                total = int(tokens[2])
            elif line.startswith("Branch Predictors"):
                for _ in range(_options.get("predictors")):
                    line = fp.readline().strip()
                    tokens = line.split()
                    token = tokens[0].split(":")[0]
                    if token.startswith("Local") or token.startswith("Global"):
                        token = "\n".join(token.split("-", 1))
                    elif token.startswith("Tournament"):
                        tour = token.split("-", 1)
                        temp = tour[1].split("-")
                        temp = ["-".join(temp[:3]), "-".join(temp[3:])]
                        token = "\n".join([tour[0], temp[0], temp[1]])
                    incorrect = int(tokens[2])
                    stats[token] = incorrect / total / 1000
            line = fp.readline()
    return stats


# def find_stats(benchmarks: Sequence[str], outputs: Sequence[str]) -> Sequence[Dict]:
#     """Function to find mpki for predictors.
    
#     Parameters
#     ----------

#     outputs: iterable of str
#         Files containing results.

#     Returns
#     -------

#     stats: iterable of dicts
#         Dictionary containing MPKI for each benchmark.
#     """
#     stats: Dict = {}
#     for benchmark, output in zip(benchmarks, outputs):
#         stats[benchmark] = find_one(output)
#     return stats


def plot_one(stats: Dict, benchmark: str, savedir: str):
    """Function to plot one benchmark.
    
    Parameters
    ----------

    dataframe: pandas DataFrame
        Contains results.

    benchmark: str
        The benchmark (for title).

    savedir: str
        Directory to save benchmark in.
    """
    labels = stats.keys()
    mpki = stats.values()
    savefile = os.path.join(savedir, f"{benchmark}.{_options.get('filetype')}")
    plt.figure(figsize=(19.2, 10.8))
    xAx = np.arange(len(labels))
    bars = plt.bar(xAx, mpki, color=_colors)
    plt.xticks([])
    plt.margins(y=0.1)
    plt.ylabel("MPKI")
    plt.legend(bars, labels, bbox_to_anchor=(1.04, 0.5), loc="center left")
    plt.title("Predictor Comparison")
    plt.savefig(savefile, bbox_inches="tight")


def plot(root: str, results: str, plots: str, benchmarks: Sequence[str]):
    """Plot results for benchmarks.
    
    Parameters
    ----------

    root: str
        The project root.

    results: str
        The results folder.

    plots: str
        The plots folder.

    benchmarks: iterable of str
        Names of benchmarks.
    """
    for benchmark in benchmarks:
        savedir = os.path.join(plots, benchmark)
        os.makedirs(savedir, exist_ok=True)
        output = os.path.join(results, benchmark, f"{benchmark}.out")
        stats = find_stats(output)
        plot_one(stats, benchmark, savedir)


if __name__ == "__main__":
    parse_arguments()
    make_colors()
    path = os.path.abspath(os.path.dirname(__file__))
    root = updir(path, 2)
    benchmarks_file = os.path.join(root, "data", "ex2", "benchmarks.txt")
    with open(benchmarks_file, "r") as fp:
        benchmarks = list(map(lambda x: x.strip(), fp.readlines()))
    benchmarks = list(map(fix_name, benchmarks))
    results = os.path.join(root, "results", "ex2")
    plots = os.path.join(root, "reports", "ex2", "plots")
    os.makedirs(plots, exist_ok=True)
    pprint(globals())
    plot(root, results, plots, benchmarks)
