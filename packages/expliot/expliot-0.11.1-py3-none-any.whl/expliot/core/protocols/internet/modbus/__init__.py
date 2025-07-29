"""Wrapper for the Modbus integration."""

from pymodbus.client import ModbusTcpClient as MBTClient
from pymodbus.exceptions import ModbusException


class ModbusTcpClient(MBTClient):
    """Wrapper for the Modbus client."""
