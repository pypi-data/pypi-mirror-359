"""Support for reading data over i2c."""

from time import time

from expliot.core.interfaces.ftdi import DEFAULT_FTDI_URL
from expliot.core.protocols.hardware.i2c import I2cEepromManager
from expliot.core.tests.test import (
    LOGNO,
    TCategory,
    Test,
    TLog,
    TTarget,
)
from expliot.plugins.i2c import DEFAULT_ADDR

DESCRIPTION = """
This plugin reads data from an I2C EEPROM chip. It needs an FTDI interface to
read data from the target EEPROM chip. You can buy an FTDI device online. If you
are interested we have an FTDI based product - 'EXPLIoT Nano' which you can
order online from www.expliot.io This plugin uses pyi2cflash package which in
turn uses pyftdi python driver for ftdi chips. For more details on supported
I2C EEPROM chips, check the readme at https://github.com/eblot/pyi2cflash Thank
you Emmanuel Blot for pyi2cflash. You may want to run it as root in case you
get a USB error related to langid."""



class I2cEepromRead(Test):
    """Plugin to read data over i2c.

    Output Format:
    There are two types of output format -
    1. When the read data is stored in a file (--wfile argument).
    2. When the read data has to be displayed instead of storing in a file.

    [
        {
            "data": "Foobar data", # Data read from the chip, this field is present
                                   # if --wfile is not specified
        },
        {
            chip_size=32768, # Size of the chip in bytes
            bytes_read=1000,
            time_taken_secs=1.67,
        }
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="readeeprom",
            summary="I2C EEPROM Reader",
            descr=DESCRIPTION,
            author="Aseem Jakhar",
            email="aseemjakhar@gmail.com",
            ref=["https://github.com/eblot/pyi2cflash"],
            category=TCategory(TCategory.I2C, TCategory.HW, TCategory.ANALYSIS),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-a",
            "--addr",
            default=DEFAULT_ADDR,
            type=int,
            help=f"Specify the start address from where data is to be "
            f"read. Default is {DEFAULT_ADDR}",
        )
        self.argparser.add_argument(
            "-l",
            "--length",
            type=int,
            help="Specify the total length of data, in bytes, to be read from "
            "the start address. If not specified, it reads till the end",
        )
        self.argparser.add_argument(
            "-u",
            "--url",
            default=DEFAULT_FTDI_URL,
            help=f"URL of the connected FTDI device. Default is {DEFAULT_FTDI_URL}. "
            f"For more details on the URL scheme check "
            f"https://eblot.github.io/pyftdi/urlscheme.html",
        )
        self.argparser.add_argument(
            "-c",
            "--chip",
            required=True,
            help="Specify the chip. Supported chips are 24AA32A, 24AA64, "
            "24AA128, 24AA256, 24AA512",
        )
        self.argparser.add_argument(
            "-w",
            "--wfile",
            help="Specify the file path where data, read from the i2c chip, "
            "is to be written. If not specified output the data on the terminal",
        )

        self.slaveaddr = 0x50

    def execute(self):
        """Execute the test."""
        TLog.generic(
            f"Reading data from i2c eeprom at address({self.args.addr}) using device({self.args.url})"
        )
        device = None
        try:
            device = I2cEepromManager.get_flash_device(
                self.args.url, self.args.chip, address=self.slaveaddr
            )
            length = self.args.length or (len(device) - self.args.addr)
            TLog.trydo(f"Reading {length} bytes from start address {self.args.addr}")
            if self.args.addr + length > len(device):
                raise IndexError("Length is out of range of the chip size")
            start_time = time()
            data = device.read(self.args.addr, length)
            end_time = time()
            if self.args.wfile:
                TLog.trydo(f"Writing data to the file ({self.args.wfile})")
                with open(self.args.wfile, "w+b") as output_file:
                    output_file.write(data)
            else:
                self.output_handler(
                    msg=f"data: {[hex(x) for x in data]}", logkwargs=LOGNO, data=data
                )
            self.output_handler(
                chip_size=len(device),
                bytes_read=len(data),
                time_taken_secs=round(end_time - start_time, 2),
            )
        except:
            self.result.exception()
        finally:
            I2cEepromManager.close(device)
