from __future__ import annotations

import logging
import os
import queue
import random
import sys
import time
import warnings
from abc import ABC
from threading import Event, Thread
from typing import IO, Callable, Iterable, NamedTuple, TextIO

from rich import box
from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderResult
from rich.file_proxy import FileProxy
from rich.layout import Layout
from rich.live import Live
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import BarColumn, Progress, Task, TaskProgressColumn, TextColumn
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text

from _view import setup_route_log

from ._util import shell_hint
from .exceptions import ViewInternalError
from .typing import LogLevel


# See https://github.com/Textualize/rich/issues/433
def _showwarning(
    message: Warning | str,
    category: type[Warning],
    filename: str,
    lineno: int,
    file: TextIO | None = None,
    line: str | None = None,
) -> None:
    msg = warnings.WarningMessage(
        message,
        category,
        filename,
        lineno,
        file,
        line,
    )

    if file is None:
        file = sys.stderr
        if file is None:
            # sys.stderr is None when run with pythonw.exe:
            # warnings get lost
            return
    text = warnings._formatwarnmsg(msg)  # type: ignore
    if file.isatty():
        Console(file=file, stderr=True).print(
            Panel(
                text,
                title=f"[bold red]{category.__name__}",
                subtitle=f"[bold green]\n{filename}, line {lineno}",
                highlight=True,
                expand=False,
            )
        )
    else:
        try:
            file.write(f"{category.__name__}: {text}")
        except OSError:
            # the file (probably stderr) is invalid - this warning gets lost.
            pass


def _warning_no_src_line(
    message: Warning | str,
    category: type[Warning],
    filename: str,
    lineno: int,
    file: TextIO | None = None,
    line: str | None = None,
) -> str:
    if (file is None and sys.stderr is not None) or file is sys.stderr:
        return str(message) + "\n"
    else:
        return f"{filename}:{lineno} {category.__name__}: {message}\n"


def format_warnings():
    warnings.showwarning = _showwarning
    warnings.formatwarning = _warning_no_src_line  # type: ignore


LCOLORS = {
    logging.DEBUG: "blue",
    logging.INFO: "green",
    logging.WARNING: "dim yellow",
    logging.ERROR: "red",
    logging.CRITICAL: "dim red",
}


class ViewFormatter(logging.Formatter):
    def formatMessage(self, record: logging.LogRecord):
        return (
            f"[bold white][[/][bold {LCOLORS[record.levelno]}]{record.levelname.lower()}[/][bold white]][/]:"
            f" {record.getMessage()}"
        )


svc = logging.getLogger("view.service")
internal = logging.getLogger("view.internal")
for lg in (svc, internal):
    lg.setLevel("INFO")
    handler = RichHandler(
        show_level=False,
        show_path=False,
        show_time=False,
        rich_tracebacks=True,
        markup=True,
    )
    handler.setFormatter(ViewFormatter())
    lg.addHandler(handler)

internal.setLevel(10000)


class RouteInfo(NamedTuple):
    status: int | str  # str for websocket states
    route: str
    method: str
    closed: bool = False


class QueueItem(NamedTuple):
    service: bool
    is_route: bool
    level: LogLevel
    message: str
    route: RouteInfo | None = None
    is_stdout: bool = False
    is_stderr: bool = False


_LIVE: bool = False
_QUEUE: queue.Queue[QueueItem] = queue.Queue()
_CLOSE = Event()


class _FileProxyWrapper(FileProxy):
    def __init__(
        self,
        console: Console,
        file: IO[str],
        qu: queue.Queue[QueueItem],
    ) -> None:
        super().__init__(console, file)
        self._queue = qu


class _StandardOutProxy(_FileProxyWrapper):
    """Wrap standard out to fancy logging."""

    def write(self, text: str) -> int:
        Internal.debug(f"stole from stdout: {text}")
        self._queue.put(QueueItem(False, False, "info", text, is_stdout=True))
        return super().write(text)


class _StandardErrProxy(_FileProxyWrapper):
    """Wrap standard error to fancy logging."""

    def write(self, text: str) -> int:
        Internal.debug(f"stole from stderr: {text}")
        self._queue.put(QueueItem(False, False, "info", text, is_stderr=True))
        return super().write(text)


def _sep(target: tuple[object, ...]):
    return " ".join([str(i) for i in target])


def _defer(msg: str, level: LogLevel, is_service: bool) -> None:
    _QUEUE.put_nowait(
        QueueItem(
            service=is_service,
            is_route=False,
            level=level,
            message=msg,
        )
    )


LOGS: dict[int, LogLevel] = {
    logging.DEBUG: "debug",
    logging.INFO: "info",
    logging.WARNING: "warning",
    logging.ERROR: "error",
    logging.CRITICAL: "critical",
}


class ServiceIntercept(logging.Filter):
    def filter(self, record: logging.LogRecord):
        if _LIVE:
            Internal.info(f"deferring service logger: {record}")
            _defer(record.getMessage(), LOGS[record.levelno], True)
            return os.environ.get("VIEW_DEBUG") == "1"
        return True


class _Logger(ABC):
    """Wrapper around the built in logger."""

    log: logging.Logger

    @staticmethod
    def _log(
        attr: Callable[..., None],
        *msg: object,
        highlight: bool = True,
        **kwargs,
    ):
        attr(
            _sep(msg),
            extra={
                "markup": True,
                **({} if highlight else {"highlighter": None}),
            },
            **kwargs,
        )

    @classmethod
    def debug(cls, *msg: object, **kwargs):
        """Write debug message."""
        cls._log(cls.log.debug, *msg, **kwargs)

    @classmethod
    def info(cls, *msg: object, **kwargs):
        """Write info message."""
        cls._log(cls.log.info, *msg, **kwargs)

    @classmethod
    def warning(cls, *msg: object, **kwargs):
        """Write warning message."""
        cls._log(cls.log.warning, *msg, **kwargs)

    @classmethod
    def error(cls, *msg: object, **kwargs):
        """Write error message."""
        cls._log(cls.log.error, *msg, **kwargs)

    @classmethod
    def critical(cls, *msg: object, **kwargs):
        """Write critical message."""
        cls._log(cls.log.critical, *msg, **kwargs)

    @classmethod
    def exception(cls, *msg: object, **kwargs):
        """Write exception."""
        cls._log(cls.log.exception, *msg, **kwargs)


class Service(_Logger):
    """Logger to be seen by the user when the app is running."""

    log = svc


class Internal(_Logger):
    """Logger to be seen by view.py developers for debugging purposes."""

    log = internal


svc.addFilter(ServiceIntercept())


def _status_color(status: int | str) -> str:
    if isinstance(status, str):
        return "bold green"

    if status >= 500:
        return "bold red"
    if status >= 400:
        return "bold purple"
    if status >= 300:
        return "bold yellow"
    if status >= 200:
        return "bold dim green"
    if status >= 100:
        return "bold blue"

    raise ViewInternalError(f"got bad status: {status}")


_METHOD_COLORS: dict[str, str] = {
    "websocket": "bold dim magenta",
    "HEAD": "bold green",
    "GET": "bold dim green",
    "POST": "bold blue",
    "PUT": "bold dim blue",
    "PATCH": "bold cyan",
    "DELETE": "bold red",
    "CONNECT": "bold magenta",
    "OPTIONS": "bold yellow",
    "TRACE": "bold dim yellow",
}


def route(path: str, status: int, method: str):
    if _LIVE:
        return _QUEUE.put_nowait(
            QueueItem(
                True,
                True,
                "info",
                "",
                route=RouteInfo(status, path, method),
            )
        )
    Service.info(
        f"[bold {_METHOD_COLORS[method]}]{method.lower()}"
        f"[/] [bold white]{path}[/]"
        f" [bold {_status_color(status)}]{status}",
        highlight=False,
    )


VIEW_TEXT = (
    r"""        _                           
       (_)                          
 __   ___  _____      ___ __  _   _ 
 \ \ / / |/ _ \ \ /\ / / '_ \| | | |
  \ V /| |  __/\ V  V /| |_) | |_| |
   \_/ |_|\___| \_/\_(_) .__/ \__, |
                       | |     __/ |
                       |_|    |___/ """,
    r"""
         _________ _______              _______          
|\     /|\__   __/(  ____ \|\     /|   (  ____ )|\     /|
| )   ( |   ) (   | (    \/| )   ( |   | (    )|( \   / )
| |   | |   | |   | (__    | | _ | |   | (____)| \ (_) / 
( (   ) )   | |   |  __)   | |( )| |   |  _____)  \   /  
 \ \_/ /    | |   | (      | || || |   | (         ) (   
  \   /  ___) (___| (____/\| () () | _ | )         | |   
   \_/   \_______/(_______/(_______)(_)|/          \_/   
                                                         
""",
    r"""
 _  _  __  ____  _  _     ____  _  _ 
/ )( \(  )(  __)/ )( \   (  _ \( \/ )
\ \/ / )(  ) _) \ /\ / _  ) __/ )  / 
 \__/ (__)(____)(_/\_)(_)(__)  (__/  
""",
    r"""
 ___      ___  __     _______  __   __  ___           _______  ___  ___  
|"  \    /"  ||" \   /"     "||"  |/  \|  "|         |   __ "\|"  \/"  | 
 \   \  //  / ||  | (: ______)|'  /    \:  |         (. |__) :)\   \  /  
  \\  \/. ./  |:  |  \/    |  |: /'        |         |:  ____/  \\  \/   
   \.    //   |.  |  // ___)_  \//  /\'    |  _____  (|  /      /   /    
    \\   /    /\  |\(:      "| /   /  \\   | ))_  ")/|__/ \    /   /     
     \__/    (__\_|_)\_______)|___/    \___|(_____((_______)  |___/      
                                                                         
""",
    r"""
                           
     _                     
 _ _|_|___ _ _ _   ___ _ _ 
| | | | -_| | | |_| . | | |
 \_/|_|___|_____|_|  _|_  |
                  |_| |___|
""",
    r"""
       _                       
 _  __(_)__ _    __  ___  __ __
| |/ / / -_) |/|/ / / _ \/ // /
|___/_/\__/|__,__(_) .__/\_, / 
                  /_/   /___/  
""",
    r"""
____    ____  __   ___________    __    ____ .______   ____    ____ 
\   \  /   / |  | |   ____\   \  /  \  /   / |   _  \  \   \  /   / 
 \   \/   /  |  | |  |__   \   \/    \/   /  |  |_)  |  \   \/   /  
  \      /   |  | |   __|   \            /   |   ___/    \_    _/   
   \    /    |  | |  |____   \    /\    / __ |  |          |  |     
    \__/     |__| |_______|   \__/  \__/ (__)| _|          |__|     
                                                                    
""",
    r"""
 __   __   __     ______     __     __     ______   __  __    
/\ \ / /  /\ \   /\  ___\   /\ \  _ \ \   /\  == \ /\ \_\ \   
\ \ \'/   \ \ \  \ \  __\   \ \ \/ ".\ \  \ \  _-/ \ \____ \  
 \ \__|    \ \_\  \ \_____\  \ \__/".~\_\  \ \_\    \/\_____\ 
  \/_/      \/_/   \/_____/   \/_/   \/_/   \/_/     \/_____/ 
                                                              
""",
    r"""
 __   __   ________  ______   __ __ __         ______   __  __    
/_/\ /_/\ /_______/\/_____/\ /_//_//_/\       /_____/\ /_/\/_/\   
\:\ \\ \ \\__.::._\/\::::_\/_\:\\:\\:\ \      \:::_ \ \\ \ \ \ \  
 \:\ \\ \ \  \::\ \  \:\/___/\\:\\:\\:\ \   ___\:(_) \ \\:\_\ \ \ 
  \:\_/.:\ \ _\::\ \__\::___\/_\:\\:\\:\ \ /__/\\: ___\/ \::::_\/ 
   \ ..::/ //__\::\__/\\:\____/\\:\\:\\:\ \\::\ \\ \ \     \::\ \ 
    \___/_( \________\/ \_____\/ \_______\/ \:_\/ \_\/      \__\/ 
                                                                  
""",
    r"""
                                                                    
            .-.                                                     
 ___  ___  ( __)   .--.    ___  ___  ___          .-..    ___  ___  
(   )(   ) (''")  /    \  (   )(   )(   )        /    \  (   )(   ) 
 | |  | |   | |  |  .-. ;  | |  | |  | |        ' .-,  ;  | |  | |  
 | |  | |   | |  |  | | |  | |  | |  | |        | |  . |  | |  | |  
 | |  | |   | |  |  |/  |  | |  | |  | |        | |  | |  | '  | |  
 | |  | |   | |  |  ' _.'  | |  | |  | |        | |  | |  '  `-' |  
 ' '  ; '   | |  |  .'.-.  | |  ; '  | |  .-.   | |  ' |   `.__. |  
  \ `' /    | |  '  `-' /  ' `-'   `-' ' (   )  | `-'  '   ___ | |  
   '_.'    (___)  `.__.'    '.__.'.__.'   `-'   | \__.'   (   )' |  
                                                | |        ; `-' '  
                                               (___)        .__.'   
""",
    r'''
            _                              _ __    _  _  
  __ __    (_)     ___   __ __ __         | '_ \  | || | 
  \ V /    | |    / -_)  \ V  V /   _     | .__/   \_, | 
  _\_/_   _|_|_   \___|   \_/\_/  _(_)_   |_|__   _|__/  
_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_| """"| 
"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-' 
''',
    r"""
  _     _   __    _____  _      _      __ __     __  __   
 /_/\ /\_\ /\_\ /\_____\/_/\  /\_\    /_/\__/\ /\  /\  /\ 
 ) ) ) ( ( \/_/( (_____/) ) )( ( (    ) ) ) ) )\ \ \/ / / 
/_/ / \ \_\ /\_\\ \__\ /_/ //\\ \_\  /_/ /_/ /  \ \__/ /  
\ \ \_/ / // / // /__/_\ \ /  \ / /_ \ \ \_\/    \__/ /   
 \ \   / /( (_(( (_____\)_) /\ (_(/_/\)_) )      / / /    
  \_\_/_/  \/_/ \/_____/\_\/  \/_/\_\/\_\/       \/_/     
                                                          
""",
    r"""
          _                                      
         (_)                                     
 _   __  __  .---.  _   _   __  _ .--.   _   __  
[ \ [  ][  |/ /__\\[ \ [ \ [  ][ '/'`\ \[ \ [  ] 
 \ \/ /  | || \__., \ \/\ \/ /_ | \__/ | \ '/ /  
  \__/  [___]'.__.'  \__/\__/(_)| ;.__/[\_:  /   
                               [__|     \__.'    
""",
    r"""
 ___      ___ ___  _______   ___       __       ________  ___    ___ 
|\  \    /  /|\  \|\  ___ \ |\  \     |\  \    |\   __  \|\  \  /  /|
\ \  \  /  / | \  \ \   __/|\ \  \    \ \  \   \ \  \|\  \ \  \/  / /
 \ \  \/  / / \ \  \ \  \_|/_\ \  \  __\ \  \   \ \   ____\ \    / / 
  \ \    / /   \ \  \ \  \_|\ \ \  \|\__\_\  \ __\ \  \___|\/  /  /  
   \ \__/ /     \ \__\ \_______\ \____________\\__\ \__\ __/  / /    
    \|__|/       \|__|\|_______|\|____________\|__|\|__||\___/ /     
                                                        \|___|/      
                                                                     
                                                                     
""",
    r"""
        __                                
.--.--.|__|.-----.--.--.--.  .-----.--.--.
|  |  ||  ||  -__|  |  |  |__|  _  |  |  |
 \___/ |__||_____|________|__|   __|___  |
                             |__|  |_____|
""",
    r"""
      _                         
 _ _ <_> ___  _ _ _    ___  _ _ 
| | || |/ ._>| | | |_ | . \| | |
|__/ |_|\___.|__/_/<_>|  _/`_. |
                      |_|  <___'
    """,
    r"""       _                               
      :_;                              
.-..-..-. .--. .-..-..-.   .---. .-..-.
: `; :: :' '_.': `; `; : _ : .; `: :; :
`.__.':_;`.__.'`.__.__.':_;: ._.'`._. ;
                           : :    .-. :
                           :_;    `._.'""",
    r"""
     .-.  .'(   )\.---.       .'(          /`-.  )\    /( 
 ,'  /  ) \  ) (   ,-._(  ,') \  )       ,' _  \ \ (_.' / 
(  ) | (  ) (   \  '-,   (  /(/ /       (  '-' (  )  _.'  
 ) './ /  \  )   ) ,-`    )    (    ,_   ) ,._.'  / /     
(  ,  (    ) \  (  ``-.  (  .'\ \  (  \ (  '     (  \     
 )/..'      )/   )..-.(   )/   )/   ).'  )/       ).'     
                                                          
""",
    r"""
_  _ ____ ____ _  _      ____ _    
|| |\|___\| __\||| \     | . \||_/\
||/ /| /  |  ]_||\ / ,-. | __/| __/
|__/ |/   |___/|/\/  '-' |/   |/   
""",
    r"""
 __    __    _____    _____   ___       ___        _____   __      __ 
 ) )  ( (   (_   _)  / ___/  (  (       )  )      (  __ \  ) \    / ( 
( (    ) )    | |   ( (__     \  \  _  /  /        ) )_) )  \ \  / /  
 \ \  / /     | |    ) __)     \  \/ \/  /        (  ___/    \ \/ /   
  \ \/ /      | |   ( (         )   _   (          ) )        \  /    
   \  /      _| |__  \ \___     \  ( )  /     __  ( (          )(     
    \/      /_____(   \____\     \_/ \_/     (__) /__\        /__\    
                                                                      
""",
    r"""
                                            
        o                                   
                                            
o    o o8 .oPYo. o   o   o    .oPYo. o    o 
Y.  .P  8 8oooo8 Y. .P. .P    8    8 8    8 
`b..d'  8 8.     `b.d'b.d'    8    8 8    8 
 `YP'   8 `Yooo'  `Y' `Y'  88 8YooP' `YooP8 
::...:::..:.....:::..::..::..:8 ....::....8 
::::::::::::::::::::::::::::::8 :::::::ooP'.
::::::::::::::::::::::::::::::..:::::::...::
""",
    r"""
          ||                      .                   
.... ... ...    ....  ... ... ...   ... ...  .... ... 
 '|.  |   ||  .|...||  ||  ||  |     ||'  ||  '|.  |  
  '|.|    ||  ||        ||| |||      ||    |   '|.|   
   '|    .||.  '|...'    |   |       ||...'     '|    
                                     ||      .. |     
                                    ''''      ''      
""",
    r"""
                                                        
         __                                             
 __  __ /\_\     __   __  __  __      _____   __  __    
/\ \/\ \\/\ \  /'__`\/\ \/\ \/\ \    /\ '__`\/\ \/\ \   
\ \ \_/ |\ \ \/\  __/\ \ \_/ \_/ \ __\ \ \L\ \ \ \_\ \  
 \ \___/  \ \_\ \____\\ \___x___/'/\_\\ \ ,__/\/`____ \ 
  \/__/    \/_/\/____/ \/__//__/  \/_/ \ \ \/  `/___/> \
                                        \ \_\     /\___/
                                         \/_/     \/__/ 
""",
    r"""
         oo                                          
                                                     
dP   .dP dP .d8888b. dP  dP  dP    88d888b. dP    dP 
88   d8' 88 88ooood8 88  88  88    88'  `88 88    88 
88 .88'  88 88.  ... 88.88b.88' dP 88.  .88 88.  .88 
8888P'   dP `88888P' 8888P Y8P  88 88Y888P' `8888P88 
                                   88            .88 
                                   dP        d8888P  
""",
    r"""
                                             
        _                                    
 _   _ (_)   __   _   _   _     _ _    _   _ 
( ) ( )| | /'__`\( ) ( ) ( )   ( '_`\ ( ) ( )
| \_/ || |(  ___/| \_/ \_/ | _ | (_) )| (_) |
`\___/'(_)`\____)`\___x___/'(_)| ,__/'`\__, |
                               | |    ( )_| |
                               (_)    `\___/'
""",
    r"""
                                                     
  __    _ ____  ______  __  __  __     _____ __    _ 
 \  \  //|    ||   ___||  \/  \|  |   |     |\ \  // 
  \  \// |    ||   ___||     /\   | _ |    _| \ \//  
   \__/  |____||______||____/  \__||_||___|   /__/   
                                                     
                                                     
""",
    r"""
       _                          
      (_)                         
 _   _ _ _____ _ _ _  ____  _   _ 
| | | | | ___ | | | ||  _ \| | | |
 \ V /| | ____| | | || |_| | |_| |
  \_/ |_|_____)\___(_)  __/ \__  |
                     |_|   (____/ 
""",
    r"""
___ _________________ __ ___    ______________
7  V  77  77     77  V  V  7    7     77  7  7
|  |  ||  ||  ___!|  |  |  |    |  -  ||  !  |
|  !  ||  ||  __|_|  !  !  |    |  ___!!_   _!
|     ||  ||     7|        |____|  7    7   7 
!_____!!__!!_____!!________!7__7!__!    !___! 
                                              
""",
    r"""
 _   _  _ ___  _   _   _____   __
| \ / || | __|| | | | | _,\ `v' /
`\ V /'| | _| | 'V' |_| v_/`. .' 
  \_/  |_|___|!_/ \_!\/_|   !_!  
""",
    r"""
        ___        __      
\  / | |__  |  |  |__) \ / 
 \/  | |___ |/\| .|     |  
                           
""",
)


COLOR = (
    "red",
    "blue",
    "pink",
    "cyan",
    "magenta",
    "yellow",
    "dim yellow",
    "dim red",
    "green",
    "dim blue",
    "dim green",
)

_LOG_COLORS: dict[LogLevel, str] = {
    "debug": "blue",
    "info": "green",
    "warning": "dim yellow",
    "error": "red",
    "critical": "dim red",
}

LMAPPINGS = {
    logging.DEBUG: Service.debug,
    logging.INFO: Service.info,
    logging.WARNING: Service.warning,
    logging.ERROR: Service.error,
    logging.CRITICAL: Service.critical,
}


class Hijack(logging.Filter):
    def filter(self, record: logging.LogRecord):
        LMAPPINGS[record.levelno](record.getMessage())
        return False


class LogPanel(Panel):
    """Panel with limit on number of lines relative to the terminal size."""

    def __init__(self, **kwargs):
        self._lines = [""]
        self._line_index = 0
        super().__init__("", **kwargs)

    def _inc(self):
        self._lines.append("")
        self._line_index += 1

    def write(self, text: str) -> None:
        """Write text to the panel."""
        for i in text:
            if i == "\n":
                self._inc()
            else:
                self._lines[self._line_index] += i

    def __rich_console__(
        self,
        console: Console,
        options: ConsoleOptions,
    ) -> RenderResult:
        height = options.height
        assert height is not None

        width = options.max_width - 2  # 2 panel characters

        while height < (len(self._lines)):
            self._lines.pop(0)
            self._line_index -= 1

        final_lines = []

        for i in self._lines:
            if len(i) < (width - 3):  # - 3 because the ellipsis
                final_lines.append(i)
            else:
                final_lines.append(f"{i[:width - 3]}...")

        self.renderable = "\n".join(final_lines)

        return super().__rich_console__(console, options)


class LogTable(Table):
    """Table with limit on number of columns relative to the terminal height."""

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        height = options.max_height
        while len(self.rows) > (height - 4):
            # - 4 because the header and footer lines
            self.rows.pop(0)
            for i in self.columns:
                i._cells.pop(0)

        return super().__rich_console__(console, options)


class Dataset:
    """
    Dataset in a graph.
    """

    def __init__(self, name: str, point_limit: int | None = None) -> None:
        """
        Args:
            name: Name of the dataset.
            point_limit: Amount of points allowed in the dataset at a time.
        """
        self.name = name
        self.points: dict[float, float] = {}
        self.point_limit = point_limit
        self.point_order: list[float] = []

    def add_point(self, x: float, y: float) -> None:
        """Add a point to the dataset.

        Args:
            x: X value.
            y: Y value.
        """
        if self.point_limit and (len(self.point_order) >= self.point_limit):
            to_del = self.point_order.pop(0)
            del self.points[to_del]

        self.point_order.append(x)
        self.points[x] = y

    def add_points(self, *args: tuple[float, float]) -> None:
        """Add multiple points to the dataset."""
        for i in args:
            self.add_point(*i)


def _heat_color(amount: float) -> str:
    """Generate a color for a percentage."""
    if amount < 20:
        return "dim blue"
    if amount < 40:
        return "cyan"
    if amount < 60:
        return "dim green"
    if amount < 80:
        return "yellow"
    if amount < 100:
        return "red"

    if amount == 100:
        return "dim red"

    raise ViewInternalError("invalid percentage")


class HeatedProgress(Progress):
    """
    Progress that changes color based on how close the bar is to completion.
    """

    def make_tasks_table(self, tasks: Iterable[Task]) -> Table:
        result = super().make_tasks_table(tasks)

        for col in result.columns:
            for cell in col._cells:
                if isinstance(cell, ProgressBar):
                    cell.complete_style = _heat_color(cell.completed)
                elif isinstance(cell, Text):
                    text = str(cell)

                    if "%" not in text:
                        continue

                    cell.stylize(_heat_color(float(text[:-1])))
        return result


def convert_kb(value: float):
    return value / 1024


def _server_logger():
    """Fancy logger implementation."""
    global _LIVE
    _LIVE = True
    table = LogTable(box=box.ROUNDED, expand=True)

    for i in ("Method", "Route", "Status"):
        table.add_column(i)

    feed = LogPanel(title="Feed")
    errors = LogPanel(title="Exceptions")
    stdout = LogPanel(title="Standard Output")
    layout = Layout()
    layout.split_row(
        Layout(name="left"),
        Layout(name="right"),
    )
    layout["left"].split_column(
        Align.center(
            Text(
                random.choice(VIEW_TEXT),
                style=f"bold {random.choice(COLOR)}",
            ),
            vertical="middle",
        ),
        errors,
        stdout,
    )
    layout["right"].split_column(
        feed,
        Layout(name="corner"),
    )
    system = HeatedProgress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(finished_style="dim red"),
        TaskProgressColumn(),
    )
    cpu = system.add_task("CPU")
    mem = system.add_task("Memory (Virtual)")
    smem = system.add_task("Memory (Swap)")
    disk = system.add_task("Disk Usage")

    try:
        import plotext as plt
    except ModuleNotFoundError:
        plt = None

    class Plot:
        """Plot renderable for rich."""

        def __init__(self, name: str, x: str, y: str) -> None:
            """Args:
            name: Title of the graph.
            x: X label of the graph.
            y: Y label of the graph."""
            if plt:
                plt.xscale("linear")
                plt.yscale("linear")

            self.title = name
            self.x_label = x
            self.y_label = y
            self.datasets: dict[str, Dataset] = {}

        def dataset(self, name: str, *, point_limit: int | None = None) -> Dataset:
            """Generate or create a new dataset.

            Args:
                name: Name of the dataset.
                point_limit: Limit on the number of points to be allowed on the graph at a time. If not set, terminal size divided by 3 is used.
            """
            found = self.datasets.get(name)
            if found:
                return found

            size = os.get_terminal_size().lines // 3

            ds = Dataset(name, point_limit=point_limit or size)
            self.datasets[name] = ds
            return ds

        def _render(self, width: int, height: int) -> None:
            if not plt:
                return

            plt.clf()
            plt.plotsize(width, height)

            for ds in self.datasets.values():
                if ds.points:
                    plt.plot(
                        [x for x in ds.points.keys()],
                        [y for y in ds.points.values()],
                        label=ds.name,
                    )

            plt.title(self.title)
            plt.xlabel(self.x_label)
            plt.ylabel(self.y_label)
            plt.theme("pro")

        def __rich_console__(
            self,
            console: Console,
            options: ConsoleOptions,
        ) -> RenderResult:
            if not plt:
                return Panel(
                    shell_hint("pip install plotext", "pip install view.py[fancy]"),
                    title="This widget needs an external library!",
                )
            self._render(options.max_width, options.max_height)
            yield Text.from_ansi(plt.build())

    layout["corner"].split_row(
        Layout(name="left_corner"),
        Layout(name="very_corner"),
    )
    network = Plot("Network", "Seconds", "Usage (KbPS)")

    try:
        import psutil
    except ModuleNotFoundError:
        psutil = None

    if psutil:
        layout["very_corner"].split_column(Panel(system, title="System"), network)
    else:
        layout["very_corner"].split_column(
            Panel(
                shell_hint("pip install plotext", "pip install view.py[fancy]"),
                title="This widget needs an external library!",
            ),
            network,
        )

    io = Plot("IO", "Seconds", "Usage (Per Second)")
    layout["left_corner"].split_column(table, io)

    console = Console()

    preserved = sys.stdout
    preserved_2 = sys.stderr
    sys.stdout = _StandardOutProxy(console, sys.stdout, _QUEUE)
    sys.stderr = _StandardErrProxy(console, sys.stderr, _QUEUE)

    def inner():
        if not psutil:
            return

        while not _CLOSE.wait(0.3):
            system.update(cpu, completed=psutil.cpu_percent())
            system.update(mem, completed=psutil.virtual_memory().percent)
            system.update(smem, completed=psutil.swap_memory().percent)
            system.update(disk, completed=psutil.disk_usage("/").percent)

    network.dataset("Upload").add_point(0, 0)
    network.dataset("Download").add_point(0, 0)

    def net():
        if not psutil:
            return

        base = time.time()
        net_io = psutil.net_io_counters()

        while not _CLOSE.wait(0.5):
            net_io2 = psutil.net_io_counters()
            ua = net_io2.bytes_sent - net_io.bytes_sent
            da = net_io2.bytes_recv - net_io.bytes_recv
            us = convert_kb(ua)
            ds = convert_kb(da)

            network.dataset("Upload").add_point(time.time() - base, us)
            network.dataset("Download").add_point(time.time() - base, ds)

            net_io = net_io2

    def io_count():
        if not psutil:
            return

        base = time.time()
        p = psutil.Process()
        pio_base = p.io_counters()

        while not _CLOSE.wait(1):
            p = psutil.Process()
            pio = p.io_counters()
            io.dataset("Read").add_point(
                time.time() - base,
                pio.read_count - pio_base.read_count,
            )
            io.dataset("Write").add_point(
                time.time() - base,
                pio.write_count - pio_base.write_count,
            )

            pio_base = pio

    for thread in (inner, net, io_count):
        Thread(target=thread, daemon=True).start()

    with Live(
        Align.center(layout),
        screen=True,
        transient=True,
        redirect_stdout=False,
        redirect_stderr=False,
        console=console,
    ) as live:
        while True:
            if _CLOSE.is_set():
                sys.stdout = preserved
                sys.stderr = preserved_2
                return

            result = _QUEUE.get()

            if result.is_stdout:
                stdout.write(result.message)
                continue

            if result.is_stderr:
                errors.write(result.message)
                continue

            if not result.is_route:
                if result.service:
                    feed.write(
                        f"[bold {_LOG_COLORS[result.level]}]"
                        f"{result.level}[/]: {result.message}\n"
                    )
            else:
                info = result.route
                assert info, "result has no route"

                if info.method == "websocket":
                    table.add_row(
                        f"[bold {_METHOD_COLORS['websocket']}]websocket[/]",
                        info.route,
                        f"[bold green]opened[/]",
                    )
                elif info.method == "websocket_closed":
                    table.add_row(
                        f"[bold {_METHOD_COLORS['websocket']}]websocket[/]",
                        info.route,
                        f"[bold red]closed[/]",
                    )
                else:
                    table.add_row(
                        f"[bold {_METHOD_COLORS[info.method]}]{info.method}[/]",
                        info.route,
                        f"[bold {_status_color(info.status)}]{info.status}[/]",
                    )

            live.update(Align.center(layout))


def _write_route(status: int | str, route: str, method_raw: str) -> None:
    method = method_raw or "websocket"
    info = RouteInfo(status, route, method)

    if _LIVE:
        _QUEUE.put_nowait(QueueItem(True, True, "info", "", info))
    else:
        if method == "websocket_closed":
            Service.info(
                f"[{_METHOD_COLORS['websocket']}]websocket[/] [white]{route}[/] [bold red]closed[/]",
                highlight=False,
            )
        elif method == "websocket":
            Service.info(
                f"[{_METHOD_COLORS['websocket']}]websocket[/] [white]{route}[/] [bold green]open[/]",
                highlight=False,
            )
        else:
            Service.info(
                f"[{_METHOD_COLORS[method]}]{method.lower()}[/] [white]{route}[/] [{_status_color(status)}]{status}[/]",
                highlight=False,
            )


setup_route_log(_write_route, Service.warning)


def enter_server():
    """Start fancy mode."""
    if _CLOSE.is_set():
        _CLOSE.clear()

    Thread(target=_server_logger, daemon=True).start()


def exit_server():
    """End fancy mode."""
    _CLOSE.set()
