"""Test for running an nmap scan."""

from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.utils.nmap import NOTIMEOUT, Nmap


class Cmd(Test):
    """Plugin for running nmap by passing original arguments.

    Output Format:
    The format is variable depending on the nmap arguments. The nmap XML output
    is converted to a dict. More details on nmap XML output can be found here:
    1. XML Output - https://nmap.org/book/output-formats-xml-output.html
    2. DTD - https://svn.nmap.org/nmap/docs/nmap.dtd
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="cmd",
            summary="Nmap Command",
            descr="This plugin allows you to run nmap by passing its original "
            "arguments via the console.",
            author="Aseem Jakhar",
            email="aseemjakhar@gmail.com",
            ref=["https://nmap.org/"],
            category=TCategory(TCategory.NMAP, TCategory.SW, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-a",
            "--args",
            required=True,
            help="Nmap command line arguments",
        )
        self.argparser.add_argument(
            "-t",
            "--timeout",
            type=int,
            default=NOTIMEOUT,
            help=f"Timeout for nmap command. Default is {NOTIMEOUT} secs, "
            f"which means no timeout",
        )

    def execute(self):
        """Execute the test."""

        TLog.success(f"nmap arguments = ({self.args.args})")
        try:
            nmp = Nmap()
            out, err = nmp.run_xmltodict_output(
                self.args.args, timeout=self.args.timeout or None
            )
            if err:
                self.result.setstatus(passed=False, reason=err)
            else:
                self.output_handler(**out)
        except:
            self.result.exception()
