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
    I2C_REFERENCE,
    VOLTAGE_RANGE,
)


class BaI2cScan(Test):
    """Test selected channels for I2C communication protocol.

    Output Format:
    [
        {
            "i2c_addr": "0x48",
            "pins": {
                        "scl": 8,
                        "sda": 9
                    }
        },
        # ... May be zero or more entries.
        # If zero i2c devices found the above dict will not be present
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="i2cscan",
            summary="I2C bus scan",
            descr="This plugin scans i2c devices and i2c pins (SCL, SDA) on "
            "the target hardware. You need to connect Bus Auditor channels "
            "(pins) to the suspected pinouts on the target pcb board. "
            "Bus Auditor pins must be connected in a sequential range and "
            "specified by the start and end pin arguments."
            "If you are seeing permission issues, kindly add a udev rule for "
            "your user for the Bus Auditor device.",
            author="Dattatray Hinge",
            email="dattatray@expliot.io",
            ref=[I2C_REFERENCE],
            category=TCategory(TCategory.BUS_AUDITOR, TCategory.HW, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
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

        if self.args.volts not in VOLTAGE_RANGE:
            self.result.setstatus(passed=False, reason="Unsupported target voltage.")
            return

        TLog.generic(f"Start Pin ({self.args.start}), End Pin ({self.args.end})")
        TLog.generic(f"Target Voltage ({self.args.volts})")

        # compute possible permutations
        ch_count = len(range(self.args.start, self.args.end + 1))
        possible_permutations = int(factorial(ch_count) / factorial(ch_count - 2))

        TLog.generic(f"Possible permutations to be tested: ({possible_permutations})")

        TLog.generic("")

        auditor = None
        found = False

        try:
            auditor = BusAuditor()
            resp = auditor.i2c_scan(self.args.start, self.args.end, self.args.volts)
            if resp:
                found = True
                TLog.success("I2C Devices:")
                for dev in resp:
                    self.output_handler(**dev)

        except:
            self.result.exception()

        finally:
            if auditor:
                auditor.close()

            if found is False:
                TLog.fail("Couldn't find i2c pins")
