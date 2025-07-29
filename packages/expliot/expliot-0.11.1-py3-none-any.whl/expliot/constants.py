"""Constants for EXPLIoT."""

from importlib.metadata import version

VERSION_NAME = "agni"

DESCRIPTION = "IoT Security Testing and Exploitation Framework"
DOCS = "https://expliot.readthedocs.io"
NAME = "EXPLIoT"
URL = "https://www.expliot.io"
BANNER_ART = r"""

          ____|   \    /    __ \    |       __  __|           __  __|
         |         \  /    |    |   |          |       __ \      |
          __|        (      ___/    |          |      /    \     |
         |         /  \    |        |          |      \    /     |
        ______|  _/   _\  _|       ______|  ______|   ____/     _|

"""

version = f"Version: {version('expliot')} - {VERSION_NAME}".center(80)
url = f"Web: {URL}".center(80)
docs = f"Documentation: {DOCS}".center(80)
by = f"by the {NAME} developers".center(80)

BANNER = f"{BANNER_ART.center(100)}\n{DESCRIPTION.center(80)}\n{version}\n{url}\n{docs}\n\n{by}"
