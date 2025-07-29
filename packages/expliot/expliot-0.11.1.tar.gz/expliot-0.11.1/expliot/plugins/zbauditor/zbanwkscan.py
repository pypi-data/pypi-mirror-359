"""Support for Zigbee network Scanner for Zigbee auditor."""

import json
import time

from expliot.core.common.exceptions import sysexcinfo
from expliot.core.protocols.radio.zigbee import ZigbeeNetworkScan
from expliot.core.tests.test import (
    LOGNO,
    TCategory,
    Test,
    TLog,
    TTarget,
)


class ZbAuditorNwkScan(Test):
    """Zigbee packet sniffer plugin.

    Output Format:
    [
        {
            'device_count': 1,
            'beacons': [
                            {
                                'source_addr': '0x0',
                                'source_panid': '0xac87',
                                'channel': 25,
                                'pan_coordinator': True,
                                'permit_joining': False,
                                'zigbee_layer': True,
                                'router_capacity': True,
                                'device_capacity': True,
                                'protocol_version': 2,
                                'stack_profile': 2,
                                'depth': 0,
                                'update_id': 0,
                                'extn_panid': [
                                                '0x0',
                                                '0x15',
                                                '0x8d',
                                                '0x0',
                                                '0x2',
                                                '0x3f',
                                                '0x60',
                                                '0x7a'
                                              ],
                                'tx_offset': '0xffffff',
                                'rssi': -57,
                                'lqi': 144
                            },
                            # ... Zero or more dict entries depending on no. of devices found
                       ]
        }
    ]

    """

    def __init__(self):
        """Initialize Zigbee Auditor."""

        super().__init__(
            name="nwkscan",
            summary="Zigbee Network Scanner",
            descr="This plugin scans 2.4 GHz network for active IEEE 802.15.4 "
            "and Zigbee devices by sending IEEE 802.15.4 beacon requests on "
            "selected channels.",
            author="Dattatray Hinge",
            email="dattatray@expliot.io",
            ref=[
                "https://www.zigbee.org/wp-content/uploads/2014/11/docs-05-3474-20-0csg-zigbee-specification.pdf"
            ],
            category=TCategory(TCategory.ZB_AUDITOR, TCategory.RD, TCategory.DISCOVERY),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-s",
            "--start",
            type=int,
            default=11,
            help="First channel to be scanned from 2.4 GHz band. "
            "If not specified, default is 11",
        )
        self.argparser.add_argument(
            "-e",
            "--end",
            type=int,
            default=26,
            help="Last channel to scanned from 2.4 GHz band"
            "if not specified, default is 26",
        )
        self.argparser.add_argument(
            "-f", "--filepath", help="file name to store network scan result as a log."
        )

        self.found = False
        self.reason = None
        self.filename = None

    @staticmethod
    def display_scan_result(result_dict):
        """TDisplay result as dictionary of network scan."""

        if "device_count" in result_dict:
            count = result_dict["device_count"]
            TLog.success(f"{'Devices found ':17} {count}")
            num_dev = 0

        if "beacons" in result_dict:
            dev_beacons = result_dict["beacons"]
            for dev in dev_beacons:
                num_dev += 1
                TLog.success(f"{'Device Number':17}: {num_dev}")
                TLog.success(f"{'Channel':17}: {dev['channel']}")
                TLog.success(f"{'Source Address':17}: {dev['source_addr']}")
                TLog.success(f"{'Source PAN ID':17}: {dev['source_panid']}")

                if "extn_panid" in dev:
                    TLog.success(
                        f"{'Extended PAN ID (Device Address)':17}: {dev['extn_panid']}"
                    )

                TLog.success(f"{'Pan Coordinator':17}: {dev['pan_coordinator']}")
                TLog.success(f"{'Permit Joining':<17}: {dev['permit_joining']}")

                if "router_capacity" in dev:
                    TLog.success(f"{'Router Capacity':17}: {dev['router_capacity']}")

                if "device_capacity" in dev:
                    TLog.success(f"{'Device Capacity':17}: {dev['device_capacity']}")

                if "protocol_version" in dev:
                    TLog.success(f"{'Protocol Version':<17}: {dev['protocol_version']}")

                if "stack_profile" in dev:
                    TLog.success(f"{'Stack Profile':17}: {dev['stack_profile']}")

                TLog.success(f"{'LQI':17}: {dev['lqi']}")
                TLog.success(f"{'RSSI':17}: {dev['rssi']}")
                TLog.generic("")

    def write_result_to_logfile(self, result_dict):
        """Write results in a file as JSON."""
        with open(self.filename, mode="w", encoding="utf-8") as write_file:
            result_json_str = json.dumps(result_dict)
            json.dump(json.loads(result_json_str), write_file, indent=4)

    def get_channel_mask(self):
        """Validate start and end scan channels and returns channel mask."""
        mask = 0x80000000  # MSB one indicate its mask
        # Calculate channel mask for scanning
        for i in range(self.args.start, self.args.end + 1):
            mask |= 1 << i  # shift 1 by channel number

        return mask

    def execute(self):
        """Execute the test."""
        if self.args.start < 11 or self.args.start > 26:
            self.result.setstatus(passed=False, reason="Invalid start channel")
            return

        if self.args.end < 11 or self.args.end > 26:
            self.result.setstatus(passed=False, reason="Invalid end channel")
            return

        if self.args.end < self.args.start:
            self.result.setstatus(passed=False, reason="Invalid start or end channel")
            return

        if self.args.filepath is not None:
            self.filename = self.args.filepath

        # Print user input
        TLog.generic(f"{'Start channel':13}: ({self.args.start})")
        TLog.generic(f"{'End channel':13}: ({self.args.end})")
        if self.filename is not None:
            TLog.generic(f"{'Log file':13}: ({self.filename})")

        TLog.generic("")

        # get channel mask
        ch_mask = self.get_channel_mask()

        try:
            # Get Network Scanner
            nwkscanner = ZigbeeNetworkScan()

            # Capture the scan start time
            start_time = time.time()

            # Start network scan with channel mask
            result_dict = nwkscanner.scan(ch_mask)

            # Capture the scan start time
            end_time = time.time()

            if result_dict is not None:
                self.found = True
                self.output_handler(logkwargs=LOGNO, **result_dict)
                # Display result on console
                self.display_scan_result(result_dict)

                TLog.success(f"{'Scan duration':17} {end_time - start_time}")
                TLog.generic("")

                # Write result in log file
                if self.filename is not None:
                    self.write_result_to_logfile(result_dict)
            else:
                self.found = False
                self.reason = "Couldn't find any Zigbee device on network"

        except:
            self.found = False
            self.reason = f"Exception caught: {sysexcinfo()}"

        finally:
            self.result.setstatus(passed=self.found, reason=self.reason)
