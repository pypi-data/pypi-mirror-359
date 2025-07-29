"""Support for reading data from SPI."""

from time import time

from expliot.core.interfaces.ftdi import DEFAULT_FTDI_URL
from expliot.core.protocols.hardware.spi import SpiFlashManager
from expliot.core.tests.test import (
    LOGNO,
    TCategory,
    Test,
    TLog,
    TTarget,
)
from expliot.plugins.spi import DEFAULT_ADDR


class SPIFlashRead(Test):
    """Test to read data from SPI.

    Output Format:
    There are two types of output format -
    1. When the read data is stored in a file (--wfile argument).
    2. When the read data has to be displayed instead of storing in a file.

    [
        {
            "chip": "Foobar XY12 8 MB",
            "size": 8388608, # in bytes
            "frequency": 30000000 # in Hz
        },
        {
            "data": "Foobar data", # Data read from the chip, this field is present
                                   # if --wfile is not specified
        },
        {
            "bytes_read":10000,
            "time_taken_secs": 0.58
        },
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="readflash",
            summary="SPI Flash Reader",
            descr="This plugin reads data from a serial flash chip that "
            "implements SPI protocol. It needs a FTDI interface to "
            "read data from the target flash chip. You can buy an "
            "FTDI device online. If you are interested we have an "
            "FTDI based product - 'EXPLIoT Nano' which you can order "
            "online from www.expliot.io. This plugin uses pyspiflash "
            "package which in turn uses pyftdi python driver for FTDI "
            "chips. For more details on supported flash chips, check "
            "the readme at https://github.com/eblot/pyspiflash. Thank "
            "you Emmanuel Blot for pyspiflash. You may want to run it "
            "as root in case you get a USB error related to langid.",
            author="Aseem Jakhar",
            email="aseemjakhar@gmail.com",
            ref=["https://github.com/eblot/pyspiflash"],
            category=TCategory(TCategory.SPI, TCategory.HW, TCategory.ANALYSIS),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-a",
            "--addr",
            default=DEFAULT_ADDR,
            type=int,
            help=f"Specify the start address from where data is to be read. "
            f"Default is {DEFAULT_ADDR}",
        )
        self.argparser.add_argument(
            "-l",
            "--length",
            type=int,
            help="Specify the total length of data, in bytes, to be read "
            "from the start address. If not specified, it reads till "
            "the end",
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
            "-f",
            "--freq",
            type=int,
            help="Specify a frequency in Hz(example: 1000000 for 1 MHz. "
            "If not, specified, default frequency of the device is "
            "used. You may want to decrease the frequency if you keep "
            "seeing FtdiError:UsbError.",
        )
        self.argparser.add_argument(
            "-w",
            "--wfile",
            help="Specify the file path where data, read from the SPI flash "
            "device, is to be written. If not specified output the data "
            "on the terminal.",
        )

    def execute(self):
        """Execute the test."""
        TLog.generic(
            f"Reading data from SPI flash at address({self.args.addr}) using device ({self.args.url})"
        )
        device = None
        try:
            device = SpiFlashManager.get_flash_device(
                self.args.url, freq=self.args.freq
            )
            length = self.args.length or (len(device) - self.args.addr)
            self.output_handler(
                chip=device, size=len(device), frequency=int(device.spi_frequency)
            )
            TLog.trydo(f"Reading {length} bytes from start address {self.args.addr}")
            if self.args.addr + length > len(device):
                raise IndexError("Length is out of range of the chip size")
            start_time = time()
            data = device.read(self.args.addr, length)
            end_time = time()
            if self.args.wfile:
                TLog.trydo(f"Writing data to the file ({self.args.wfile})")
                with open(self.args.wfile, "w+b") as local_file:
                    local_file.write(data)
            else:
                self.output_handler(
                    msg=f"data: {[hex(x) for x in data]}", logkwargs=LOGNO, data=data
                )
            self.output_handler(
                bytes_read=len(data), time_taken_secs=round(end_time - start_time, 2)
            )
        except:
            self.result.exception()
        finally:
            SpiFlashManager.close(device)
