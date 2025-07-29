"""Support for Zigbee packet replay for zigbee auditor."""

import time

from expliot.core.common.exceptions import sysexcinfo
from expliot.core.common.pcaphelper import wireshark_dump_reader
from expliot.core.protocols.radio.dot154 import Dot154Radio
from expliot.core.protocols.radio.dot154.dot154_utils import (
    get_dst_pan_from_packet,
    is_ack_packet,
)
from expliot.core.tests.test import TCategory, Test, TLog, TTarget


class ZbAuditorReplay(Test):
    """Zigbee packet dump replay plugin.

    Output Format:
    [
        {
            "packets_received": 0,
            "packets_transmitted": 9
        }
    ]
    """

    DELAYMS = 200

    def __init__(self):
        """Initialize the replay."""

        super().__init__(
            name="replay",
            summary="IEEE 802.15.4 packet replay",
            descr="This plugin reads packets from the specified pcap file and "
            "replays them on the specified channel.",
            author="Dattatray Hinge",
            email="dattatray@expliot.io",
            ref=[
                "https://www.zigbee.org/wp-content/uploads/2014/11/docs-05-3474-20-0csg-zigbee-specification.pdf"
            ],
            category=TCategory(TCategory.ZB_AUDITOR, TCategory.RD, TCategory.EXPLOIT),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-c",
            "--channel",
            type=int,
            required=True,
            help="IEEE 802.15.4 2.4 GHz channel to inject with Zigbee packets",
        )
        self.argparser.add_argument(
            "-f",
            "--pcapfile",
            required=True,
            help="PCAP file name to be read for Zigbee packets",
        )
        self.argparser.add_argument(
            "-p",
            "--pan",
            type=lambda x: int(x, 0),
            help="Replays packets for destination PAN address. Prefix 0x if pan is hex"
            "Example:- 0x12ab or 4779",
        )
        self.argparser.add_argument(
            "-d",
            "--delay",
            type=int,
            default=self.DELAYMS,
            help=f"Inter-packet delay in milliseconds. Default is {self.DELAYMS}",
        )

    def execute(self):
        """Execute the test."""
        dst_pan = None
        send_packet = False
        radio = None

        # Get Destination PAN address
        if self.args.pan:
            dst_pan = self.args.pan

        delay_sec = self.args.delay / 1000

        TLog.generic(f"{'Channel':13}: ({self.args.channel})")
        TLog.generic(f"{'File':13}: ({self.args.pcapfile})")
        TLog.generic(f"{'Delay (seconds)':13}: ({delay_sec})")
        if dst_pan:
            TLog.generic(f"{'Destination PAN':15}: ({hex(dst_pan)})")
        TLog.generic("")

        try:
            radio = Dot154Radio()
            radio.radio_on()
            radio.set_channel(self.args.channel)

            for packet in wireshark_dump_reader(self.args.pcapfile):
                if not dst_pan and not is_ack_packet(packet) or dst_pan and dst_pan == get_dst_pan_from_packet(packet):
                    send_packet = True

                if send_packet:
                    radio.inject_raw_packet(packet[0:-2])
                    send_packet = False
                    time.sleep(delay_sec)

        except:
            self.result.setstatus(
                passed=False, reason=f"Exception caught: {sysexcinfo()}"
            )

        finally:
            # Turn OFF radio and exit
            if radio:
                self.output_handler(
                    packets_received=radio.get_received_packets(),
                    packets_transmitted=radio.get_transmitted_packets(),
                )
                radio.radio_off()
