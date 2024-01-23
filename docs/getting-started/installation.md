# Installation

## System Requirements

view.py requires [CPython](https://python.org/downloads/) 3.8 or above.

!!! question "What is CPython?"

    CPython is the reference/official implementation of Python. If you downloaded Python through [python.org](https://python.org) or some sort of system package manager (e.g. `apt`, `pacman`, `brew`), it's probably CPython.

## Installing with a Virtual Environment (Recommended)

### Windows

```
> py -3 -m venv .venv
> .\.venv\activate
> pip install view.py
```

### Linux/macOS

```
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install view.py
```

!!! question "Why a virtual environment?"

    view.py is a large package with lots of dependencies, as well as a big [extension module](https://docs.python.org/3/extending/extending.html). If you have no idea what a virtual environment is or why they're useful, take a look at [Python's documentation](https://docs.python.org/3/library/venv.html).

## Installing via Pip

### Windows

```
> py -3 -m pip install -U view.py
```

### Linux/macOS

```
$ python3 -m pip install view.py
```

## Development Version

```
$ git clone https://github.com/ZeroIntensity/view.py
$ cd view.py
$ pip install .
```

## Finalizing

To ensure you've installed view.py correctly, run the `view` command:

```
$ view
Welcome to view.py!
Docs: https://view.zintensity.dev
GitHub: https://github.com/ZeroIntensity/view.py
```

If this doesn't work properly, try executing via Python:

```
$ python3 -m view
Welcome to view.py!
Docs: https://view.zintensity.dev
GitHub: https://github.com/ZeroIntensity/view.py
```
