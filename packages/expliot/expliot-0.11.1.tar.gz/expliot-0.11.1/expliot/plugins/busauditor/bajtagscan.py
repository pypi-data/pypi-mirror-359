"""Support for Bus Auditor Device Information."""

from math import factorial

from expliot.core.interfaces.busauditor import BusAuditor
from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.plugins.busauditor import (
    CHANNEL_MAX,
    CHANNEL_MIN,
    DEFAFULT_END,
    DEFAFULT_START,
    DEFAULT_VOLTS,
    JTAG_REFERENCE,
    VOLTAGE_RANGE,
)


class BaJtagScan(Test):
    """Test selected channels for JTAG communication protocol.

    Output Format:
    # TRST is optional, dependes if it is included by user in jtag scan
    [
        {
            "jtag_idcode": "0x4ba00477",
            "pins": {
                        "trst": 4,      # "TRST" pin included in jtag scan
                        "tck": 0,
                        "tms": 1,
                        "tdo": 3,
                        "tdi": 2
                    }
        },
        {
            "jtag_idcode": "0x06431041",
            "pins": {
                        "trst": 4,      # "TRST" pin included in jtag scan
                        "tck": 0,
                        "tms": 1,
                        "tdo": 3,
                        "tdi": 2
                    }
        },
        # ... May be zero or more entries.
        # If zero JTAG devices found the above dict will not be present
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="jtagscan",
            summary="JTAG port scan",
            descr="This plugin scans JTAG port for JTAG device id, JTAG pins "
            "(TMS, TCK, TDO, TDI and TRST) on the target hardware. "
            "TRST pin scan is optional and depends upon target HW, if TRST pin "
            "is active on target HW, then it must be include in scan. "
            "You need to connect Bus Auditor channels (pins) to the suspected "
            "pinouts on the target pcb board. "
            "Bus Auditor pins must be connected in a sequential range and "
            "specified by the start and end pin arguments. "
            "If you are seeing permission issues, kindly add a udev rule for "
            "your user for the Bus Auditor device.",
            author="Dattatray Hinge",
            email="dattatray@expliot.io",
            ref=[JTAG_REFERENCE],
            category=TCategory(TCategory.BUS_AUDITOR, TCategory.HW, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-i",
            "--include_trst",
            action="store_true",
            help="Include TRST pin in scan",
        )

        self.argparser.add_argument(
            "-s",
            "--start",
            type=int,
            default=DEFAFULT_START,
            help=f"First Bus Auditor channel for the scan. If not specified, "
            f"it will start the scan from channel ({DEFAFULT_START})",
        )

        self.argparser.add_argument(
            "-e",
            "--end",
            type=int,
            default=DEFAFULT_END,
            help=f"Last Bus Auditor channel for the scan. If not specified, "
            f"it will scan until channel ({DEFAFULT_END}).",
        )

        self.argparser.add_argument(
            "-v",
            "--volts",
            type=str,
            default=DEFAULT_VOLTS,
            help=f"Target voltage out. "
            f"Supported target volts are ({VOLTAGE_RANGE[0]}), ({VOLTAGE_RANGE[1]}), and ({VOLTAGE_RANGE[2]}) If not specified, "
            f"target voltage will be ({DEFAULT_VOLTS}) volts.",
        )

    def execute(self):
        """Execute the test."""
        possible_permutations = 0

        # Start channel cannot be less than zero or greater than 15
        if self.args.start < CHANNEL_MIN or self.args.start > CHANNEL_MAX:
            self.result.setstatus(passed=False, reason="Invalid start channel.")
            return

        # End channel cannot be less than zero or greater than 15
        if self.args.end < CHANNEL_MIN or self.args.end > CHANNEL_MAX:
            self.result.setstatus(passed=False, reason="Invalid end channel.")
            return

        # Start and End channel cannot be same
        if self.args.start == self.args.end:
            self.result.setstatus(passed=False, reason="Same start and end channel.")
            return

        # Start > End channel
        if self.args.start > self.args.end:
            self.result.setstatus(
                passed=False, reason="Start channel greater than end channel."
            )
            return

        # compute possible permutations
        ch_count = len(range(self.args.start, self.args.end + 1))
        if self.args.include_trst:
            if ch_count < 5:
                self.result.setstatus(
                    passed=False, reason="Minimum 5 pins required for jtag scan."
                )
                return
            possible_permutations = int(factorial(ch_count) / factorial(ch_count - 5))
        else:
            if ch_count < 4:
                self.result.setstatus(
                    passed=False, reason="Minimum 4 pins required for jtag scan."
                )
                return
            possible_permutations = int(factorial(ch_count) / factorial(ch_count - 4))

        if self.args.volts not in VOLTAGE_RANGE:
            self.result.setstatus(passed=False, reason="Unsupported target voltage.")
            return

        TLog.generic(f"Start Pin ({self.args.start}), End Pin ({self.args.end})")
        TLog.generic(f"Target Voltage ({self.args.volts})")

        if self.args.include_trst:
            TLog.generic("TRST pin included in scan")
        else:
            TLog.generic("TRST pin excluded from scan")

        TLog.generic(f"Possible permutations to be tested: ({possible_permutations})")

        TLog.generic("")

        auditor = None
        found = False

        try:
            auditor = BusAuditor()
            resp = auditor.jtag_scan(
                self.args.start, self.args.end, self.args.volts, self.args.include_trst
            )
            if resp:
                found = True
                TLog.success("JTAG Devices:")
                for dev in resp:
                    self.output_handler(**dev)

        except:
            self.result.exception()

        finally:
            if auditor:
                auditor.close()

            if found is False:
                TLog.fail("Couldn't find jtag pins")
