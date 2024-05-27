# Installation

## System Requirements

view.py requires [CPython](https://python.org/downloads/) 3.8 or above.

!!! question "What is CPython?"

    CPython is the reference/official implementation of Python. If you downloaded Python through [python.org](https://python.org) or some sort of system package manager (e.g. `apt`, `pacman`, `brew`), it's probably CPython.

## Installing with Pipx (Recommended)

[pipx](https://pipx.pypa.io/stable/) can install CLIs into isolated environments. view.py recommends using `pipx` for installation, and then using `view init` to initialize a virtual environment in projects. For example:

```
$ pipx install view.py
... pipx output
$ view init
```

## Installing via Pip

```
$ pip install view.py
```

## Development Version

```
$ pip install git+https://github.com/ZeroIntensity/view.py
```

## Finalizing

To ensure you've installed view.py correctly, run the `view` command:

```
$ view
```

If this doesn't work properly, try executing via Python:

```
$ python3 -m view
```
