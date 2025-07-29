import logging

import obsws_python as obsws
from clypi import Command, arg
from typing_extensions import override

from .errors import SimpleRecorderError

logging.basicConfig(level=logging.disable())


class Split(Command):
    """Split the current recording into a new file."""

    host: str = arg(inherited=True)
    port: int = arg(inherited=True)
    password: str = arg(inherited=True)

    @override
    async def run(self):
        """Run the split command."""
        try:
            with obsws.ReqClient(
                host=self.host, port=self.port, password=self.password, timeout=3
            ) as client:
                resp = client.get_record_status()
                if not resp.output_active:
                    raise SimpleRecorderError("No active recording to split.")

                client.split_record_file()
                print("Recording split successfully.")
        except (ConnectionRefusedError, TimeoutError):
            raise SimpleRecorderError("Failed to connect to OBS. Is it running?")
        except obsws.error.OBSSDKRequestError as e:
            if e.code == 702:
                raise SimpleRecorderError(
                    "Unable to split file, please check your OBS settings."
                )
            else:
                raise SimpleRecorderError(f"Error: {e.code} - {e.message}")
