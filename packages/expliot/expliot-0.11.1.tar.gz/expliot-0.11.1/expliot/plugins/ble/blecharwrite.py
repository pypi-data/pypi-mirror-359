"""Test the possibility to write data to a Bluetooth LE device."""

from expliot.core.protocols.radio.ble import (
    ADDR_TYPE_PUBLIC,
    ADDR_TYPE_RANDOM,
    BlePeripheral,
)
from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.plugins.ble import BLE_REF


class BleCharWrite(Test):
    """Plugin to write characteristic data to a Bluetooth LE device.

    Output Format:
    There is no output for this plugin
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="writechar",
            summary="BLE Characteristic writer",
            descr="This test allows you to write a value to a characteristic on a BLE peripheral device",
            author="Aseem Jakhar",
            email="aseemjakhar@gmail.com",
            ref=[BLE_REF],
            category=TCategory(TCategory.BLE, TCategory.RD, TCategory.ANALYSIS),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-a",
            "--addr",
            required=True,
            help="Address of BLE device whose characteristic value will be written to",
        )
        self.argparser.add_argument(
            "-n",
            "--handle",
            required=True,
            type=lambda x: int(x, 0),
            help="Specify the handle to write to. Prefix 0x if handle is hex",
        )
        self.argparser.add_argument(
            "-w", "--value", required=True, help="Specify the value to write"
        )
        self.argparser.add_argument(
            "-r",
            "--randaddrtype",
            action="store_true",
            help="Use LE address type random. If not specified use address type public",
        )
        self.argparser.add_argument(
            "-s",
            "--noresponse",
            action="store_true",
            help="Send write command instead of write request i.e. no response, if specified",
        )

    def execute(self):
        """Execute the test."""
        TLog.generic(
            f"Writing the value ({self.args.value}) to handle ({hex(self.args.handle)}) on BLE device ({self.args.addr})"
        )
        device = BlePeripheral()
        try:
            device.connect(
                self.args.addr,
                addrType=(
                    ADDR_TYPE_RANDOM if self.args.randaddrtype else ADDR_TYPE_PUBLIC
                ),
            )
            device.writeCharacteristic(
                self.args.handle,
                bytes.fromhex(self.args.value),
                withResponse=(not self.args.noresponse),
            )
        except:
            self.result.exception()
        finally:
            device.disconnect()
