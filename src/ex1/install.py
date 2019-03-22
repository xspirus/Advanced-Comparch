#!/usr/bin/env python3

import os
import shutil
import tarfile
import wget
from ..helper.dirs import updir
import subprocess as sp

PIN = "https://software.intel.com/sites/landingpage/pintool/downloads/pin-3.6-97554-g31f0a167d-gcc-linux.tar.gz"
PARSEC_CORE = "http://parsec.cs.princeton.edu/download/3.0/parsec-3.0-core.tar.gz"
PARSEC_SIM = "http://parsec.cs.princeton.edu/download/3.0/parsec-3.0-input-sim.tar.gz"
CSLAB_HELPCODE = "http://www.cslab.ece.ntua.gr/courses/advcomparch/files/askiseis/advanced-ca-Spring-2019-ask1-helpcode.tar.gz"

def cslab_helpcode(root, pin):
    """Function to install cslab helpcode.

    Parameters
    ----------

    root: str
        The root path of this project.

    pin: str
        The pin path.

    Returns
    -------

    path: str
        The path where the code was installed.
    """
    cslab = os.path.join(root, "CSLab")
    os.makedirs(cslab, exist_ok=True)
    tarname = wget.download(CSLAB_HELPCODE, out=os.path.join(cslab, "ex1.tar.gz"))
    tar = tarfile.open(name=tarname, mode="r:gz")
    dirname = tar.next().name
    tar.extractall(path=cslab)
    tar.close()
    os.remove(tarname)
    os.rename(os.path.join(cslab, dirname), os.path.join(cslab, "ex1"))
    pintool = os.path.join(cslab, "ex1", "pintool")
    cmd = f"make clean PIN_ROOT={pin}".split()
    sp.run(cmd, cwd=pintool)
    cmd = f"make PIN_ROOT={pin}".split()
    sp.run(cmd, cwd=pintool)
    return os.path.join(cslab, "ex1")


def pintool(root):
    """Function to install pin.

    Parameters
    ----------

    root: str
        The root path of this project.

    Returns
    -------

    path: str
        The path pin was installed.
    """
    path = os.path.basename(PIN)
    path = "-".join(path.split("-")[:2])
    tarname = wget.download(PIN, out=os.path.join(root, f"{path}.tar.gz"))
    tar = tarfile.open(tarname, mode="r:gz")
    dirname = tar.next().name
    tar.extractall(path=root)
    tar.close()
    os.remove(tarname)
    os.rename(os.path.join(root, dirname), os.path.join(root, path))
    return os.path.join(root, path)


def parsec(root):
    """Function to install parsec benchmarks.

    Parameters
    ----------

    root: str
        The root path of this project.

    Returns
    -------

    path: str
        The path pin was installed.
    """
    tarname = wget.download(PARSEC_CORE, out=os.path.join(root, "parsec-core.tar.gz"))
    tar = tarfile.open(tarname, mode="r:gz")
    tar.extractall(path=root)
    tar.close()
    os.remove(tarname)
    tarname = wget.download(PARSEC_SIM, out=os.path.join(root, "parsec-sim.tar.gz"))
    tar = tarfile.open(tarname, mode="r:gz")
    dirname = tar.next().name
    tar.extractall(path=root)
    tar.close()
    os.remove(tarname)
    return os.path.join(root, dirname)


def cslab_fixes(sims, cslab):
    """Function to apply cslab scripts.

    Parameters
    ----------

    sims: str
        Parsec path.

    cslab: str
        CSLab helpcode path.
    """
    script = "cslab_process_parsec_benchmarks.sh"
    script = os.path.join(cslab, script)
    cmd = ["sh", script]
    sp.run(cmd, cwd=sims)


def build_parsec(sims, build, packages):
    """Function to build parsec benchmarks.

    Parameters
    ----------

    sims: str
        Parsec path.
    
    build: str
        File path containing build command for parsec.

    packages: str
        File path containing packages needed.
    """
    cmd = "sudo apt update".split()
    sp.run(cmd)
    with open(packages, "r") as fp:
        packages = list(map(lambda x: x.strip(), fp.readlines()))
    cmd = "sudo apt install -y".split()
    cmd.extend(packages)
    sp.run(cmd)
    with open(build, "r") as fp:
        cmd = fp.read().strip().split()
    sp.run(cmd, cwd=sims)


def create_workspace(sims, cslab):
    """Function to create parsec workspace.

    Parameters
    ----------

    sims: str
        Parsec path.

    cslab: str
        CSLab helpcode path.
    """
    script = "cslab_create_parsec_workspace.sh"
    script = os.path.join(cslab, script)
    cmd = ["sh", script]
    sp.run(cmd, cwd=sims)
    workspace = os.path.join(sims, "parsec_workspace")
    shutil.copyfile(os.path.join(cslab, "cmds_simlarge.txt"),
                    os.path.join(workspace, "cmds_simlarge.txt"))


if __name__ == "__main__":
    path = os.path.abspath(os.path.dirname(__file__))
    root = updir(path, 2)
    pin = pintool(root)
    cslab = cslab_helpcode(root, pin)
    sims = parsec(root)
    print()
    cslab_fixes(sims, cslab)
    build_parsec(sims, 
                 os.path.join(root, "docs", "ex1", "build.txt"),
                 os.path.join(root, "docs", "ex1", "packages.txt"))
    create_workspace(sims, cslab)
