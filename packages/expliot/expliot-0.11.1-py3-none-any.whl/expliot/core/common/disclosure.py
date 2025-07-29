"""Helper to collecting details about EXPLIoT itself."""

import json
import os
import platform
from collections import namedtuple
from datetime import datetime
from importlib.metadata import version

import distro
import pyudev


class Disclosure:
    """Plugin for collecting details about EXPLIoT itself."""

    def __init__(self):
        """Initialize the test."""
        self.expliot_release = version("expliot")

        self.python_release = platform.python_version()

        self.distribution = f"{distro.name()} {distro.version()} {distro.codename()}"

        self.host_platform = platform.platform()

        self.host_processor = platform.machine()

        self.host_architecture = (
            f"{platform.architecture()[0]}, {platform.architecture()[1]}"
        )

        self.root = os.geteuid() == 0

        self.usb_devices = json.dumps(check_usb_devices(), indent=4)

        self.bus_auditor = check_hardware_presence("0483", "ba20")

        self.zigbee_auditor = check_hardware_presence("1915", "521a")

        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def output(self):
        """Generate the output based on the available attributes."""
        attributes = {
            key: value
            for key, value in self.__dict__.items()
            if not callable(value) and not key.startswith("_")
        }
        Attributes = namedtuple("Attributes", attributes.keys())
        return Attributes(**attributes)

    def _human_readable(self, snake_str: str) -> str:
        """Convert snake_case string to Title Case."""
        components = snake_str.split("_")
        return " ".join(x.capitalize() for x in components)

    def __str__(self):
        """Return a formatted string representation of the attribute values."""
        attributes = self.output()
        formatted_attributes = "\n".join(
            [
                f"{self._human_readable(key)}: {value}"
                for key, value in attributes._asdict().items()
            ]
        )
        return f"{formatted_attributes}"


def check_usb_devices() -> dict:
    """List all attached USB devices."""
    context = pyudev.Context()
    devices = {}

    for device in context.list_devices(subsystem="usb", DEVTYPE="usb_device"):

        product_name = device.get("ID_MODEL_FROM_DATABASE", "Unknown")

        if product_name in ["2.0 root hub", "3.0 root hub"]:
            continue

        for tty_device in context.list_devices(subsystem="tty"):
            if tty_device.parent and tty_device.parent.device_path.startswith(
                device.device_path
            ):
                devices[tty_device.device_node] = {
                    "id": f"{device.get('ID_VENDOR_ID', 'Unknown')}:{device.get('ID_MODEL_ID', 'Unknown')}",
                    "device_node": device.device_node,
                    "manufacturer": device.get("ID_VENDOR_FROM_DATABASE", "Unknown"),
                    "product": device.get("ID_MODEL_FROM_DATABASE", "Unknown"),
                    "device_path": device.device_path,
                }

    return devices


def check_hardware_presence(vendor_id: str, product_id: str) -> bool:
    """Check if a hardware unit is connected to the host via USB."""
    context = pyudev.Context()
    enumerator = pyudev.Enumerator(context).match_subsystem("usb")
    present = False

    for device in enumerator:
        if device.device_type == "usb_device":
            vendor_id_device = device.attributes.get("idVendor")
            product_id_device = device.attributes.get("idProduct")

            if (
                vendor_id_device.decode("utf-8") == vendor_id
                and product_id_device.decode("utf-8") == product_id
            ):
                present = True
                break

    return present
