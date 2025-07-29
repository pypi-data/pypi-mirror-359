"""Test for collecting details about EXPLIoT itself."""

from expliot.core.common.disclosure import Disclosure
from expliot.core.tests.test import (
    LOGPRETTY,
    TCategory,
    Test,
    TLog,
    TTarget,
)


class Self(Test):
    """Plugin for collecting details about EXPLIoT itself."""

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="self",
            summary="EXPLIoT details",
            descr="This plugin collects details about EXPLIoT itself and the"
            "system it runs on.",
            author="Fabian Affolter",
            email="fabian@affolter-engineering.ch",
            ref=["https://expliot.io"],
            category=TCategory(TCategory.DISCLOSURE, TCategory.SW, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

    def execute(self):
        """Execute the test."""

        disclosure = Disclosure()
        TLog.generic("Display details about EXPLIoT itself")

        try:
            disclosure = Disclosure()
            self.output_handler(msg=f"\n{disclosure}", logkwargs=LOGPRETTY)
        except:
            self.result.exception()
