# Advanced Computer Architecture
* NTUA 8th Semester Lesson

## Prerequisites
* [pipenv](https://pypi.org/project/pipenv/)

## Before Exercises
Run the following:
```bash
make deps
pipenv install -e src
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
