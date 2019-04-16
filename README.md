# Advanced Computer Architecture
* NTUA 8th Semester Lesson

## Prerequisites
* [pipenv](https://pypi.org/project/pipenv/)

## Before Exercises
Run the following:
```bash
make deps
```

## Exercise 1
Run the following to install pintool and parsec:
```bash
pipenv run python -m src.ex1.install
```
If you want to make the pintool again run:
```bash
pipenv run python -m make 1
```
To run L1 configuration:
```bash
pipenv run python -m src.ex1.run L1
```
Run `pipenv run python -m src.ex1.run --help` for options.

### Plots
Run `pipenv run python -m src.ex1.plot --help` to check how to make plots.

### 10 Million Instructions
Run `pipenv run python -m src.ex1.run10m --time`.
Run `pipenv run python -m src.ex1.plot10m` to plot results.

## Exercise 2
Run the following to install pintool:
```bash
pipenv run python -m make 2
```

Run the following to run benchmarks:
```bash
pipenv run python -m src.ex2.run --time
```
