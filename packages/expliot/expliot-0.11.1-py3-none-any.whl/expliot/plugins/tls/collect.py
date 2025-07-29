"""Test for collecting TLS/SSL details."""

from expliot.core.protocols.internet.tls import TLSDetailsFetcher
from expliot.core.tests.test import (
    LOGPRETTY,
    TCategory,
    Test,
    TLog,
    TTarget,
)


class TLS(Test):
    """Plugin for fetching TLS/SSL details."""

    def __init__(self):
        """Initialize the test."""

        super().__init__(
            name="collect",
            summary="TLS/SSL collector",
            descr="This plugin collects basic information about a"
            "TLS/SSL-enabled service.",
            author="Fabian Affolter",
            email="fabian@affolter-engineering.ch",
            ref=["https://datatracker.ietf.org/doc/html/rfc5246"],
            category=TCategory(TCategory.TLS, TCategory.SW, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-t",
            "--target",
            required=True,
            help="Target host",
        )
        self.argparser.add_argument(
            "-p",
            "--port",
            type=int,
            default=443,
            help="Port to test, defults to 443",
        )

    def execute(self):
        """Execute the test."""

        TLog.success(f"TLS target = ({self.args.target})")

        try:
            fetcher = TLSDetailsFetcher(self.args.target, self.args.port)
            details = fetcher.get_tls_details()
            self.output_handler(**details)
        except:
            self.result.setstatus(passed=False, reason="Host/port is not reachable")
