"""Test for reading data from the CAN bus."""

from binascii import hexlify

from expliot.core.protocols.hardware.can import CanBus
from expliot.core.tests.test import (
    LOGNORMAL,
    TCategory,
    Test,
    TLog,
    TTarget,
)


class CANRead(Test):
    """Test for reading from the CAN bus.

    Output Format:
    There are two types of format
    1. Read all types of can messages
    2. Where arbitration id is specified for reading those can messages

    1. Read all
    [
        {
            "count":1,
            "arbitration_id":"0x161",
            "data":"000005500108000d"
        },
        # ... May be more than one message
    ]

    2. Read only for specific arbitration id
    [
        {
            "count":28,
            "data":"000000013d"
        },
        # ... May be more than one message
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="readcan",
            summary="CAN bus reader",
            descr="This plugin allows you to read message(s) from the CAN bus. "
            "As of now it uses socketcan but if you want to extend it to"
            " other interfaces, just open an issue on the official"
            " expliot project repository.",
            author="Aseem Jakhar",
            email="aseemjakhar@gmail.com",
            ref=["https://en.wikipedia.org/wiki/CAN_bus"],
            category=TCategory(TCategory.CAN, TCategory.HW, TCategory.ANALYSIS),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-i", "--iface", default="vcan0", help="Interface to use. Default is vcan0"
        )
        self.argparser.add_argument(
            "-a",
            "--arbitid",
            type=lambda x: int(x, 0),
            help="Show messages of the specified arbitration ID only. For hex "
            "value prefix it with 0x",
        )
        self.argparser.add_argument(
            "-c",
            "--count",
            type=int,
            default=10,
            help="Specify the count of messages to read from the CANBus. Default is 10",
        )
        self.argparser.add_argument(
            "-t",
            "--timeout",
            type=float,
            help="Specify the time, in seconds, to wait for each read. Default "
            "is to wait forever. You may use float values as well i.e. 0.5",
        )

    def execute(self):
        """Execute the test."""
        TLog.generic(
            f"Reading ({self.args.count}) messages from CANbus on interface({self.args.iface})"
        )

        try:
            bus = None
            if self.args.count < 1:
                raise ValueError(f"Illegal count value {self.args.count}")
            bus = CanBus(interface="socketcan", channel=self.args.iface)
            for cnt in range(1, self.args.count + 1):
                message = bus.recv(timeout=self.args.timeout)
                if message is None:
                    raise TimeoutError("Timed out while waiting for CAN message")
                if self.args.arbitid:
                    if self.args.arbitid == message.arbitration_id:
                        self.output_handler(
                            logkwargs=LOGNORMAL,
                            count=cnt,
                            data=hexlify(message.data).decode(),
                        )
                else:
                    self.output_handler(
                        logkwargs=LOGNORMAL,
                        count=cnt,
                        arbitration_id="0x{message.arbitration_id:x}",
                        data=hexlify(message.data).decode(),
                    )
        except:
            self.result.exception()
        finally:
            if bus:
                bus.shutdown()
