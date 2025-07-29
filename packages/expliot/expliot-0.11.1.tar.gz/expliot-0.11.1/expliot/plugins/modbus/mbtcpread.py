"""Support for reading data from Modbus over TCP."""

from expliot.core.protocols.internet.modbus import (
    ModbusException,
    ModbusTcpClient,
)
from expliot.core.tests.test import (
    LOGNO,
    TCategory,
    Test,
    TLog,
    TTarget,
)
from expliot.plugins.modbus import (
    COIL,
    DEFAULT_ADDR,
    DEFAULT_COUNT,
    DEFAULT_UNITID,
    DINPUT,
    HREG,
    IREG,
    MODBUS_PORT,
    MODBUS_REFERENCE,
    READ_ITEMS,
)


class MBTcpRead(Test):
    """Test for reading data from Modbus over TCP.

    Output Format:
    [
        {"addr": 2, "value": 1},
        # ... May be more entries
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="readtcp",
            summary="Modbus TCP Reader",
            descr="This plugin reads the item (coil, discrete input, holding "
            "and input register) values from a Modbus server.",
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
            help=f"The item to read from. {COIL} = {READ_ITEMS[COIL]}, {DINPUT} = {READ_ITEMS[DINPUT]}, {HREG} = {READ_ITEMS[HREG]}, {IREG} = {READ_ITEMS[IREG]}. Default is {COIL}",
        )
        self.argparser.add_argument(
            "-a",
            "--address",
            default=DEFAULT_ADDR,
            type=int,
            help=f"The start address of item to read from. Default is {DEFAULT_ADDR}",
        )
        self.argparser.add_argument(
            "-c",
            "--count",
            default=DEFAULT_COUNT,
            type=int,
            help=f"The count of items to read. Default is {DEFAULT_COUNT}",
        )
        self.argparser.add_argument(
            "-u",
            "--unit",
            default=DEFAULT_UNITID,
            type=int,
            help=f"The Unit ID of the slave on the server to read from. "
            f"The default is {DEFAULT_UNITID}",
        )

    def execute(self):
        """Execute the test."""
        modbus_client = ModbusTcpClient(self.args.rhost, port=self.args.rport)

        try:
            if self.args.item < 0 or self.args.item >= len(READ_ITEMS):
                raise AttributeError(f"Unknown --item specified ({self.args.item})")

            TLog.generic(
                f"Sending read command to Modbus Server ({self.args.rhost}) on port ({self.args.rport})"
            )
            TLog.generic(
                f"(item={READ_ITEMS[self.args.item]})(address={self.args.address})(count={self.args.count})(unit={self.args.unit})"
            )
            modbus_client.connect()
            if self.args.item == COIL:
                response = modbus_client.read_coils(
                    self.args.address, self.args.count, unit=self.args.unit
                )
                if response.isError() is True:
                    raise ModbusException(str(response))
                values = response.bits
            elif self.args.item == DINPUT:
                response = modbus_client.read_discrete_inputs(
                    self.args.address, self.args.count, unit=self.args.unit
                )
                if response.isError() is True:
                    raise ModbusException(str(response))
                values = response.bits
            elif self.args.item == HREG:
                response = modbus_client.read_holding_registers(
                    self.args.address, self.args.count, unit=self.args.unit
                )
                if response.isError() is True:
                    raise ModbusException(str(response))
                values = response.registers
            elif self.args.item == IREG:
                response = modbus_client.read_input_registers(
                    self.args.address, self.args.count, unit=self.args.unit
                )
                if response.isError() is True:
                    raise ModbusException(str(response))
                values = response.registers
            else:
                raise AttributeError(f"Unknown --item specified ({self.args.item})")
            for entry in range(self.args.count):
                addr = self.args.address + entry
                self.output_handler(
                    msg=f"({READ_ITEMS[self.args.item]}[{addr}]={values[entry]})",
                    logkwargs=LOGNO,
                    addr=addr,
                    value=values[entry],
                )
        except:
            self.result.exception()
        finally:
            modbus_client.close()
