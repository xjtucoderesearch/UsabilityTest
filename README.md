# Automated Usability Test

## Before start

You need:

- A computer with `Windows 10` as operating system

- `Java` latest installed (>= 15) and can be accessed via the environment path
  > Some tools depends on JRE to run.

- `SciTools Understand` installed and can be accessed via the environment path
  > Apply for a free student license on the [website](https://www.scitools.com/student/) if you don't have a one.

- `Sourcetrail` installed and can be accessed via the environment path
  > Follow the guidance on [tools/#_INSTALL_THIS_sourcetrail/README.doc](./tools/%23_INSTALL_THIS_sourcetrail/README.doc) to install and operate.

  > **WARNING** SourceTrail depends on Python **^3.8** to analyze python projects, if you don'y explicitly assign a python executable path while creating a project, then you would better make sure a Python 3.8 is accessable via the environment.

- Allow git to use long file name:

  ```sh
  $ git config --system core.longpaths true
  ```

- Python package `psutil` installed
  > This is used for memory usage profiling

## Run test, with only one command

```sh
$ python do.py <lang> <range> [only] [-t --timeout <range(300, 3600)>]
```

where,

* `lang` can be one of
  * `java`
  * `cpp`
  * `python`

* `range` can be one of
  * a number `n`, refers to n-th project in the list
  * a range `a-b`, refers to projects from  a-th to b-th

> * Usually you don't need to set this, `only` can be one of
>   * `enre`: Runs `ENRE-<lang>` only
>   * `depends`: Runs `Depends` only
>   * `understand`: Runs `Understand` only
>   * `clone`: Just clone the repositories
>   * `loc`: Just count the LoC

* `-t --timeout` limits the maximum duration a process can take, this feature is activated only when a valid number is given.

We highly encourage you to run this script under `Windows Terminal` + `PowerShell`, this conbination suits the modern world on Windows platform.

Press ENTER, Booooooom, you are free to afk.

## Submit results

We want all newly generated files under these directories:

* `logs/`
* `time-records/`

## To make the fucking Sourcetrail run, i deleted following environment variables:

PYTHONHOME C:\Users\ThisRabbit\miniforge3
PYTHONPATH C:\Users\ThisRabbit\miniforge3
PATH C:\Users\ThisRabbit\miniforge3 C:\Users\ThisRabbit\miniforge3\Scripts

