# Logging

## Logger API

Logging in view.py is a bit more complicated than other libraries. The original `logging` module that comes with Python wasn't really fun to deal with, so a more abstracted API on top of it was designed.

`_Logger` is an abstract class to give a nicer, more object oriented approach to logging. To create a new `_Logger` ready class, simply inherit from it and specify a `logging.Logger object`:

```py
class MyLogger(_Logger):
    log = logging.getLogger("MyLogger")
```

`MyLogger` above could then be used like so:

```py
MyLogger.info("something")
```

::: view._logging._Logger

view.py has two loggers, `Service` and `Internal`. `Service` is meant for general app information that is sent to the user, whereas `Internal` is meant for debugging.

::: view._logging.Service
::: view._logging.Internal

## Warnings

Warnings have been customized for view.py to give a prettier output for the user. The implementation is taken from [this issue](https://github.com/Textualize/rich/issues/433).

## Fancy Mode

Fancy mode is a special output for running an app. It's powered by [rich live](https://rich.readthedocs.io/en/stable/live.html) and has some specially designed components. It wraps things like I/O counts to a graph for more eye candy at runtime. It can be started via `enter_server` and ended via `exit_server`.

Once online, special `QueueItem` objects are sent to `_QUEUE`, which is handled by the live display and updated on screen.

::: view._logging
