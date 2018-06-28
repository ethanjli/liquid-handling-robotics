"""IOPins channels of board protocol."""

# Standard imports
import logging
from abc import abstractmethod
from typing import Iterable, List, Optional

# Local package imports
from lhrhost.messaging.presentation import Message, MessageReceiver
from lhrhost.protocol import Command, CommandIssuer
from lhrhost.util.interfaces import InterfaceClass
from lhrhost.util.printing import Printer

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# Receipt of IOPins

class IOPinsReceiver(object, metaclass=InterfaceClass):
    """Interface for a class which receives io_pin events.

    This may include versions from self or from other sources.
    """

    @abstractmethod
    def on_io_pin_digital(self, pin: int, payload: int) -> None:
        """Receive and handle a digital io_pin."""
        pass

    @abstractmethod
    def on_io_pin_analog(self, pin: int, payload: int) -> None:
        """Receive and handle a digital io_pin."""
        pass


# Type-checking names
_IOPinsReceivers = Iterable[IOPinsReceiver]


# Printing

class IOPinsPrinter(IOPinsReceiver, Printer):
    """Simple class which prints received serialized messages."""

    def on_io_pin_digital(self, pin: int, payload: int) -> None:
        """Receive and handle a digital pin reading."""
        self.print('Pin {}: {}'.format(
            pin, 'HIGH' if payload else 'LOW'
        ))

    def on_io_pin_analog(self, pin: int, payload: int) -> None:
        """Receive and handle an analog pin reading."""
        self.print('Pin A{}: {}'.format(pin, payload))


class IOPinsProtocol(MessageReceiver, CommandIssuer):
    """Determines and prints protocol version."""

    def __init__(
        self, io_pins_receivers: Optional[_IOPinsReceivers]=None, **kwargs
    ):
        """Initialize member variables."""
        super().__init__(**kwargs)
        self.__io_pins_receivers: List[IOPinsReceiver] = []
        if io_pins_receivers:
            self.__io_pins_receivers = [receiver for receiver in io_pins_receivers]

    def notify_io_pins_receivers_digital(self, pin: int, payload: int) -> None:
        """Notify all receivers of received digital pin reading."""
        for receiver in self.__io_pins_receivers:
            receiver.on_io_pin_digital(pin, payload)

    def notify_io_pins_receivers_analog(self, pin: int, payload: int) -> None:
        """Notify all receivers of received analog pin reading."""
        for receiver in self.__io_pins_receivers:
            receiver.on_io_pin_analog(pin, payload)

    # Commands

    async def request_io_pin_digital(self, pin: int):
        """Send an digital pin read request command to message receivers."""
        # TODO: validate the pin
        await self.notify_message_receivers(Message('id{}'.format(pin)))

    async def request_io_pin_analog(self, pin: int):
        """Send an analog pin read request command to message receivers."""
        # TODO: validate the pin
        await self.notify_message_receivers(Message('ia{}'.format(pin)))

    async def request_wait_io_pin_digital(self, pin: int):
        """Send an digital pin read request command to message receivers."""
        # TODO: validate the pin
        channel = 'id{}'.format(pin)
        await self.issue_command(Command(Message(channel), [channel]))

    async def request_wait_io_pin_analog(self, pin: int):
        """Send a analog pin read request command to message receivers."""
        # TODO: validate the pin
        channel = 'ia{}'.format(pin)
        await self.issue_command(Command(Message(channel), [channel]))

    # Implement DeserializedMessageReceiver

    async def on_message(self, message: Message) -> None:
        """Handle received message.

        Only handles known io_pin messages.
        """
        if message.payload is None:
            return
        # TODO: validate the channel name
        if message.channel.startswith('id'):
            self.notify_io_pins_receivers_digital(int(message.channel[2:]), message.payload)
        elif message.channel.startswith('ia'):
            self.notify_io_pins_receivers_analog(int(message.channel[2:]), message.payload)
        self.on_response(message.channel)
