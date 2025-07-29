import obsws_python as obsws
from clypi import Command, Positional, arg
from typing_extensions import override

from .errors import SimpleRecorderError
from .styler import highlight


class Chapter(Command):
    """Create a chapter in the current recording."""

    chapter_name: Positional[str] = arg(
        help="Name of the chapter to create.",
        prompt="Enter the name for the chapter.",
        default="unnamed",
    )
    host: str = arg(inherited=True)
    port: int = arg(inherited=True)
    password: str = arg(inherited=True)

    @override
    async def run(self):
        """Run the chapter command."""
        try:
            with obsws.ReqClient(
                host=self.host, port=self.port, password=self.password, timeout=3
            ) as client:
                resp = client.get_record_status()
                if not resp.output_active:
                    raise SimpleRecorderError(
                        "No active recording to create a chapter."
                    )

                # Allow OBS to set unnamed chapters (it will increment the name)
                if self.chapter_name == "unnamed":
                    client.create_record_chapter()
                else:
                    client.create_record_chapter(self.chapter_name)
                print(f"Chapter {highlight(self.chapter_name)} created successfully.")
        except (ConnectionRefusedError, TimeoutError):
            raise SimpleRecorderError("Failed to connect to OBS. Is it running?")
        except obsws.error.OBSSDKRequestError as e:
            if e.code == 702:
                raise SimpleRecorderError(
                    "Unable to create chapter, please check your OBS settings."
                )
            else:
                raise SimpleRecorderError(f"Error: {e}")
