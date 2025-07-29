import logging

from clypi import ClypiConfig, ClypiException, Command, arg, configure
from typing_extensions import override

from .chapter import Chapter
from .directory import Directory
from .errors import SimpleRecorderError
from .gui import SimpleRecorderWindow
from .pause import Pause
from .resume import Resume
from .split import Split
from .start import Start
from .stop import Stop

config = ClypiConfig(
    nice_errors=(SimpleRecorderError,),
)
configure(config)

themes = [
    "Light Purple",
    "Neutral Blue",
    "Reds",
    "Sandy Beach",
    "Kayak",
    "Light Blue 2",
]


def theme_parser(value: str) -> str:
    """Parse the theme argument."""
    if value not in themes:
        raise ClypiException(
            f"Invalid theme: {value}. Available themes: {', '.join(themes)}"
        )
    return value


SUBCOMMANDS = Start | Stop | Pause | Resume | Split | Chapter | Directory


class SimpleRecorder(Command):
    subcommand: SUBCOMMANDS | None = None
    host: str = arg(default="localhost", env="OBS_HOST", help="OBS WebSocket host")
    port: int = arg(default=4455, env="OBS_PORT", help="OBS WebSocket port")
    password: str | None = arg(
        default=None, env="OBS_PASSWORD", help="OBS WebSocket password"
    )
    theme: str = arg(
        default="Reds",
        parser=theme_parser,
        env="OBS_THEME",
        help=f"GUI theme ({', '.join(themes)})",
    )
    debug: bool = arg(
        default=False,
        help="Enable debug logging",
        hidden=True,
    )

    @override
    async def pre_run_hook(self):
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.disable())

    @override
    async def run(self):
        """Run the Simple Recorder GUI."""
        window = SimpleRecorderWindow(self.host, self.port, self.password, self.theme)
        await window.run()


def run():
    """Run the application."""
    SimpleRecorder.parse().start()
