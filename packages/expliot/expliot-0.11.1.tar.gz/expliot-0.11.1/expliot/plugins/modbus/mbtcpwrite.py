"""Support for writing data to Modbus over TCP."""

from expliot.core.protocols.internet.modbus import (
    ModbusException,
    ModbusTcpClient,
)
from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.plugins.modbus import (
    COIL,
    DEFAULT_ADDR,
    DEFAULT_COUNT,
    DEFAULT_UNITID,
    MODBUS_PORT,
    MODBUS_REFERENCE,
    REG,
    WRITE_ITEMS,
)


class MBTcpWrite(Test):
    """Test for writing data to Modbus over TCP.

    Output Format:
    There is no ouput.
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="writetcp",
            summary="Modbus TCP Writer",
            descr="This plugin writes the item (coil, register) values to a "
            "Modbus server.",
            author="Aseem Jakhar",
            email="aseemjakhar@gmail.com",
            ref=MODBUS_REFERENCE,
            category=TCategory(TCategory.MODBUS, TCategory.SW, TCategory.ANALYSIS),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-r",
            "--rhost",
            required=True,
            help="The hostname/IP address of the Modbus server",
        )
        self.argparser.add_argument(
            "-p",
            "--rport",
            default=MODBUS_PORT,
            type=int,
            help=f"The port number of the Modbus server. Default is {MODBUS_PORT}",
        )
        self.argparser.add_argument(
            "-i",
            "--item",
            default=COIL,
            type=int,
            help=f"The item to write to. {COIL} = {WRITE_ITEMS[COIL]}, {REG} = {WRITE_ITEMS[REG]}. Default is {COIL}",
        )
        self.argparser.add_argument(
            "-a",
            "--address",
            default=DEFAULT_ADDR,
            type=int,
            help=f"The start address of item to write to. The "
            f"default is {DEFAULT_ADDR}",
        )
        self.argparser.add_argument(
            "-c",
            "--count",
            default=DEFAULT_COUNT,
            type=int,
            help=f"The count of items to write. Default is {DEFAULT_COUNT}",
        )
        self.argparser.add_argument(
            "-u",
            "--unit",
            default=DEFAULT_UNITID,
            type=int,
            help=f"The unit ID of the slave on the server to write to. "
            f"The default is {DEFAULT_UNITID}",
        )
        self.argparser.add_argument(
            "-w", "--value", required=True, type=int, help="The value to write"
        )

    def execute(self):
        """Execute the test."""
        modbus_client = ModbusTcpClient(self.args.rhost, port=self.args.rport)

        try:
            if self.args.item < 0 or self.args.item >= len(WRITE_ITEMS):
                raise AttributeError(f"Unknown --item specified ({self.args.item})")
            if self.args.count < 1:
                raise AttributeError(f"Invalid --count specified ({self.args.count})")

            TLog.generic(
                f"Sending write command to Modbus Server ({self.args.rhost}) on port ({self.args.rport})"
            )
            TLog.generic(
                f"(item={WRITE_ITEMS[self.args.item]})(address={self.args.address})(count={self.args.count})(unit={self.args.unit})"
            )
            modbus_client.connect()
            if self.args.item == COIL:
                value = bool(self.args.value != 0)
                TLog.trydo(f"Writing value(s): {value}")
                response = modbus_client.write_coils(
                    self.args.address, [value] * self.args.count, unit=self.args.unit
                )
                if response.isError() is True:
                    raise ModbusException(str(response))
            elif self.args.item == REG:
                TLog.trydo(f"Writing value(s): {self.args.value}")
                response = modbus_client.write_registers(
                    self.args.address,
                    [self.args.value] * self.args.count,
                    unit=self.args.unit,
                )
                if response.isError() is True:
                    raise ModbusException(str(response))
            else:
                raise AttributeError(f"Unknown --item specified ({self.args.item})")
            TLog.success("Values successfully written")
        except:
            self.result.exception()
        finally:
            modbus_client.close()
