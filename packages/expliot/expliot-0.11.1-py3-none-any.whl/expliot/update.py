"""Update module to check for updates and downloads."""

import json
from importlib.metadata import version
from os import mkdir
from os.path import expanduser, isdir, isfile
from time import time
from urllib.request import urlopen

from expliot.core.tests.test import TLog


class Updater:
    """Updater class to check for updates and downloads."""

    LOCAL_JSON = """
    {

        "software": {
            "last_check_time": "0",
            "last_check_version": "0"
        }
    }
"""

    def __init__(self):
        """Initialize the Updater class."""

        self._url = "http://localhost:62321/update"
        # self._url = "https://expliot.org/update"
        self._version = version("expliot")
        self._dir = expanduser("~/.expliot")
        self._cjson = f"{self._dir}/local.json"
        self._sjson = None

        self.create_conf()

    def create_conf(self):
        """Create the local directory and files.

        @return None
        """
        if not isdir(self._dir):
            TLog.success(f"Creating directory {self._dir}")
            mkdir(self._dir)
        if not isfile(self._cjson):
            TLog.success(f"Creating file {self._cjson}")
            with open(self._cjson, mode="w", encoding="utf-8") as f:
                f.write(Updater.LOCAL_JSON)
        else:
            with open(self._cjson, encoding="utf-8") as f:
                conf = json.load(f)
            if conf is None or not conf:
                with open(self._cjson, mode="w", encoding="utf-8") as f:
                    f.write(Updater.LOCAL_JSON)

    def read_conf(self):
        """Read the local configuration file.

        @return dict
        """
        with open(self._cjson, encoding="utf-8") as f:
            conf = json.load(f)
        if conf is None or not conf:
            self.create_conf()
            conf = json.loads(Updater.LOCAL_JSON)
        return conf

    def check(self):
        """Check for updates.

        @return bool True if update available, False otherwise
        """
        # try:
        #     # Don't check for updates if last check was less than 24 hours ago
        #     conf = self.read_conf()
        #     ctime = time()
        #     ltime = float(conf["software"]["last_check_time"])
        #     if ctime - ltime < 24 * 60 * 60:
        #         # TLog.success(f"Last update check was less than 24 hrs ago. Skipping")
        #         return False
        #     TLog.trydo(f"Checking for updates at {self._url}")
        #     with urlopen(self._url, timeout=4.0) as response:
        #         self._sjson = json.loads(response.read())
        #         version = self._sjson["software"]["version"]
        #         conf["software"]["last_check_time"] = ctime
        #         conf["software"]["last_check_version"] = version
        #         with open(self._cjson, mode="w", encoding="utf-8") as f:
        #             json.dump(conf, f)
        #         if version > self._version:
        #             TLog.success(f"\x1b[1;31mUpdate available: {version}\x1b[0m")
        #             TLog.success("Please run '\x1b[1;31m$(sudo) pip3 install expliot --upgrade\x1b[0m' to update")
        #             return True
        #         return False
        # except BaseException as ex:
        #     TLog.fail(f"Exception occured while checking for updates: {ex.__class__.__name__} -> {ex}")
        #     return False
        return False


if __name__ == "__main__":
    updater = Updater()
    if updater.check():
        print("Update available")
    else:
        print("No update available")
