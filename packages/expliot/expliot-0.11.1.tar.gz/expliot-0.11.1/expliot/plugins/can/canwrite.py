"""Test for writing data to the CAN bus."""

from time import sleep

from expliot.core.protocols.hardware.can import CanBus, CanMessage
from expliot.core.tests.test import TCategory, Test, TLog, TTarget


class CANWrite(Test):
    """Test for writing from the CAN bus.

    Output Format:
    [
        {"message_sent": 1},
        # ... May be more than one message sent
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="writecan",
            summary="CAN bus writer",
            descr="This plugin allows you to write message(s) on the CAN bus "
            "e.g, send a data  frame. As of now it uses socketcan but if "
            "you want to extend it to other interfaces, just open an issue "
            "on the official expliot project repository.",
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
            required=True,
            type=lambda x: int(x, 0),
            help="Specify the arbitration ID. For hex value prefix it with 0x",
        )
        self.argparser.add_argument(
            "-e",
            "--exid",
            action="store_true",
            help="Specify this option if using extended format --arbitid",
        )
        self.argparser.add_argument(
            "-d",
            "--data",
            required=True,
            help="Specify the data to write, as hex stream, without the "
            "0x prefix. For ex. deadbeef",
        )
        self.argparser.add_argument(
            "-c",
            "--count",
            type=int,
            default=1,
            help="Specify the no. of messages to write. Default is 1",
        )
        self.argparser.add_argument(
            "-w",
            "--wait",
            type=float,
            help="Specify the wait time, in seconds, between each consecutive "
            "message write. Default is to not wait between writes. You "
            "may use float values as well, e.g. 0.5",
        )

    def execute(self):
        """Execute tht test."""
        TLog.generic(
            f"Writing to CANbus on interface({self.args.iface}), arbitration id(0x{self.args.arbitid:x}), "
            f"extended?({self.args.exid}) data({self.args.data})"
        )

        try:
            bus = None
            if self.args.count < 1:
                raise ValueError(f"Illegal count value {self.args.count}")
            bus = CanBus(interface="socketcan", channel=self.args.iface)
            message = CanMessage(
                arbitration_id=self.args.arbitid,
                is_extended_id=self.args.exid,
                data=list(bytes.fromhex(self.args.data)),
            )
            for count in range(1, self.args.count + 1):
                bus.send(message)
                self.output_handler(message_sent=count)
                if self.args.wait and count < self.args.count:
                    sleep(self.args.wait)
        except:
            self.result.exception()
        finally:
            if bus:
                bus.shutdown()
