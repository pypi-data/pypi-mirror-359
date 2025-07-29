"""Support for grabbing TCP banners."""

import socket

from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.plugins.tcp import DEFAULT_TCP_TIMEOUT


class Banner(Test):
    """Test for possible banners."""

    def __init__(self):
        """Initialize the banner grabbing."""

        super().__init__(
            name="banner",
            summary="TCP ports banner grabber",
            descr="This plugin tries to grab a given amount of lines "
            "from an open TCP port. Or better known as banner grabbing.",
            author="Fabian Affolter",
            email="fabian@affolter-engineering.ch",
            ref=["https://www.ietf.org/rfc/rfc793.txt"],
            category=TCategory(TCategory.TCP, TCategory.SW, TCategory.DISCOVERY),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )
        self.argparser.add_argument(
            "-r", "--rhost", required=True, help="IP address of the device or host"
        )
        self.argparser.add_argument(
            "-v", "--verbose", action="store_true", help="Show verbose output"
        )
        self.argparser.add_argument(
            "-l",
            "--lines",
            default=5,
            type=int,
            help="Number of line to get. Defaults to 5.",
        )
        self.argparser.add_argument(
            "-s",
            "--start_port",
            default=0,
            type=int,
            help="Port to start. Defaults to 0.",
        )
        self.argparser.add_argument(
            "-e",
            "--end_port",
            default=65535,
            type=int,
            help="Last port to check. Defaults to 65535.",
        )
        self.argparser.add_argument(
            "-t",
            "--timeout",
            default=DEFAULT_TCP_TIMEOUT,
            type=float,
            help=f"Timeout in seconds for each port. "
            f"Default is {DEFAULT_TCP_TIMEOUT} second.",
        )

    def execute(self):
        """Execute the test."""
        TLog.generic(f"Test in range {self.args.start_port}-{self.args.end_port} on {self.args.rhost}")
        results = {}

        for port in range(self.args.start_port, self.args.end_port + 1):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.args.timeout)
                try:
                    sock.connect((self.args.rhost, port))
                    lines = read_lines_from_socket(
                        sock, self.args.lines, self.args.verbose
                    )
                    results[port] = lines if lines else "No response from service"
                except (TimeoutError, OSError) as error:
                    if self.args.verbose:
                        TLog.fail(
                            f"Could not connect to {self.args.rhost}:{port} - {error}"
                        )

        self.output_handler(results=results)


def read_lines_from_socket(sock, num_lines, verbose):
    """Read a given amount of line after the connection is made."""
    lines = []
    try:
        for _ in range(num_lines):
            line = sock.recv(1024).decode("utf-8")
            if not line:
                break
            lines.append(line.strip())
    except OSError as error:
        if verbose:
            TLog.fail(f"Socket error: {error}")
    return lines
