from __future__ import annotations

import asyncio
import logging
import queue
import random
import re
import sys
import warnings
from abc import ABC
from threading import Thread
from typing import Callable, NamedTuple, TextIO

from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from typing_extensions import Literal

UVICORN_ROUTE_REGEX = re.compile(r'.*"(.+) (\/.*) .+" ([0-9]{1,3}).*')


# see https://github.com/Textualize/rich/issues/433


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


class UvicornHijack(logging.Filter):
    def filter(self, record: logging.LogRecord):
        if record.exc_text:
            Service.error(record.exc_text)
        STATUS_TO_SVC = {
            logging.DEBUG: Service.debug,
            logging.INFO: Service.info,
            logging.WARNING: Service.warning,
            logging.ERROR: Service.error,
            logging.CRITICAL: Service.critical,
        }
        message = record.getMessage()
        match = UVICORN_ROUTE_REGEX.match(message)

        if match:
            # its a route message
            method = match.group(1)
            path = match.group(2)
            status = int(match.group(3))
            route(path, status, method)
        else:
            STATUS_TO_SVC[record.levelno](message)
        return False


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
            f"[bold {LCOLORS[record.levelno]}]{record.levelname.lower()}[/]:"
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
    )
    handler.setFormatter(ViewFormatter())
    lg.addHandler(handler)


internal.setLevel(10000)


class RouteInfo(NamedTuple):
    status: int
    route: str
    method: str


class QueueItem(NamedTuple):
    service: bool
    is_route: bool
    level: LogLevel
    message: str
    route: RouteInfo | None = None


_LIVE: bool = False
_QUEUE: queue.Queue[QueueItem] = queue.Queue()
_CLOSE = asyncio.Event()

LogLevel = Literal["debug", "info", "warning", "error", "critical"]


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
            return False
        return True


class _Logger(ABC):
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
        cls._log(cls.log.debug, *msg, **kwargs)

    @classmethod
    def info(cls, *msg: object, **kwargs):
        cls._log(cls.log.info, *msg, **kwargs)

    @classmethod
    def warning(cls, *msg: object, **kwargs):
        cls._log(cls.log.warning, *msg, **kwargs)

    @classmethod
    def error(cls, *msg: object, **kwargs):
        cls._log(cls.log.error, *msg, **kwargs)

    @classmethod
    def critical(cls, *msg: object, **kwargs):
        cls._log(cls.log.critical, *msg, **kwargs)

    @classmethod
    def exception(cls, *msg: object, **kwargs):
        cls._log(cls.log.exception, *msg, **kwargs)


class Service(_Logger):
    log = svc


class Internal(_Logger):
    log = internal


svc.addFilter(ServiceIntercept())


def _status_color(status: int) -> str:
    if status >= 500:
        return "red"
    if status >= 400:
        return "purple"
    if status >= 300:
        return "yellow"
    if status >= 200:
        return "green"
    if status >= 100:
        return "blue"

    raise ValueError(f"got bad status: {status}")


_METHOD_COLORS: dict[str, str] = {
    "HEAD": "dim green",
    "GET": "green",
    "POST": "blue",
    "PUT": "dim blue",
    "PATCH": "cyan",
    "DELETE": "red",
    "CONNECT": "magenta",
    "OPTIONS": "yellow",
    "TRACE": "dim yellow",
}


def route(path: str, status: int, method: str):
    if _LIVE:
        return _QUEUE.put_nowait(
            QueueItem(
                True, True, "info", "", route=RouteInfo(status, path, method)
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


COLOR = ("red", "blue", "pink", "white", "yellow")

_LOG_COLORS: dict[LogLevel, str] = {
    "debug": "blue",
    "info": "green",
    "warning": "dim yellow",
    "error": "red",
    "critical": "dim red",
}


def _server_logger():
    global _LIVE
    _LIVE = True
    table = Table(box=box.HORIZONTALS)

    for i in ("method", "route", "status"):
        table.add_column(i)

    panel = Panel("", title="Feed")
    group = Group(
        Align.center(
            Text(
                random.choice(VIEW_TEXT),
                style=f"bold {random.choice(COLOR)}",
            )
        ),
        Align.center(table),
        panel,
    )
    lines = []

    with Live(Align.center(group), screen=True, transient=True):
        while True:
            if _CLOSE.is_set():
                break
            result = _QUEUE.get()
            if not result.is_route:
                if result.service:
                    assert isinstance(panel.renderable, str)
                    lines.append(
                        f"[bold {_LOG_COLORS[result.level]}]"
                        f"{result.level}[/]: {result.message}"
                    )
                    panel.renderable = "\n".join(lines)
            else:
                info = result.route
                assert info, "result has no route"

                table.add_row(
                    f"[bold {_METHOD_COLORS[info.method]}]{info.method}[/]",
                    info.route,
                    f"[bold {_status_color(info.status)}]{info.status}[/]",
                )


def enter_server():
    Thread(target=_server_logger).start()

    if _CLOSE.is_set():
        _CLOSE.clear()


def exit_server():
    _CLOSE.set()
