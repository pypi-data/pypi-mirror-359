"""Wrapper for CANbus communication."""

from can import Message
from can.interface import Bus as CanBus

# python-can 4.3.0 has changed the Bus class to a factory function.
# To make it compatible with the existing plugins, we will rename the
# function as CanBus and remove the class definition.
# class CanBus(Bus):
#    """A simple wrapper around python-can Bus class."""
#    pass

class CanMessage(Message):
    """A simple wrapper around python-can Message class."""
