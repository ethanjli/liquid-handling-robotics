"""IOPins channels of board protocol."""

# Standard imports
import logging
from abc import abstractmethod
from typing import Iterable, List, Optional

# Local package imports
from lhrhost.messaging.presentation import Message
from lhrhost.protocol import (
    ChannelHandlerTreeChildNode, ChannelHandlerTreeNode,
    Command, CommandIssuer
)
from lhrhost.util.interfaces import InterfaceClass
from lhrhost.util.printing import Printer

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# Receipt of IOPins

class IOPinsReceiver(object, metaclass=InterfaceClass):
    """Interface for a class which receives IOPins/* events."""

    @abstractmethod
    async def on_io_pin_digital(self, pin: int, payload: int) -> None:
        """Receive and handle a IOPins/Digital/* response."""
        pass

    @abstractmethod
    async def on_io_pin_analog(self, pin: int, payload: int) -> None:
        """Receive and handle an IOPins/Analog/* response."""
        pass


# Type-checking names
_IOPinsReceivers = Iterable[IOPinsReceiver]


# Printing

class IOPinsPrinter(IOPinsReceiver, Printer):
    """Simple class which prints received IOPins/* responses."""

    async def on_io_pin_digital(self, pin: int, payload: int) -> None:
        """Receive and handle a IOPins/Digital/* response."""
        self.print('Pin {}: {}'.format(
            pin, 'HIGH' if payload else 'LOW'
        ))

    async def on_io_pin_analog(self, pin: int, payload: int) -> None:
        """Receive and handle an IOPins/Analog/* response."""
        self.print('Pin A{}: {}'.format(pin, payload))


class IOPinsTypeProtocol(ChannelHandlerTreeChildNode, CommandIssuer):
    """Reads IO pins of the specified type."""

    def __init__(self, *args, **kwargs):
        """Initialize member variables."""
        super().__init__(*args, **kwargs)
        self.command_receivers = self.parent.command_receivers
        self.io_pins_receivers = self.parent.io_pins_receivers

    async def notify_io_pins_receivers(self, pin: int, payload: int) -> None:
        """Notify all receivers of received IOPins/_/_ response."""
        for receiver in self.io_pins_receivers:
            if self.node_channel == 'Analog':
                await receiver.on_io_pin_analog(pin, payload)
            elif self.node_channel == 'Digital':
                await receiver.on_io_pin_analog(pin, payload)
            else:
                raise NotImplementedError(
                    'Unsupported channel {}!'.format(self.channel_path)
                )

    # Commands

    async def request(self, pin: int):
        """Send a IOPins/_/_ request command to message receivers."""
        # TODO: validate the pin number
        message = Message('{}{}'.format(self.name_path, pin))
        await self.issue_command(Command(message))

    # Implement ChannelHandlerTreeNode

    async def on_any_message(self, message):
        """Handle any message whether or not it is recognized as by the node."""
        if message.payload is None:
            return
        self.on_response(message.channel)

    async def on_received_message(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the node."""
        if message.payload is None:
            return
        await self.notify_io_pins_receivers(channel_name_remainder, message.payload)


class IOPinsProtocol(ChannelHandlerTreeNode, CommandIssuer):
    """Reads digital and analog IO pins."""

    def __init__(
        self, io_pins_receivers: Optional[_IOPinsReceivers]=None, **kwargs
    ):
        """Initialize member variables."""
        super().__init__(**kwargs)

        self.io_pins_receivers: List[IOPinsReceiver] = []
        if io_pins_receivers:
            self.io_pins_receivers = [receiver for receiver in io_pins_receivers]

        self.analog = IOPinsTypeProtocol(self, 'Analog', 'a', **kwargs)
        self.digital = IOPinsTypeProtocol(self, 'Digital', 'd', **kwargs)

    # Implement ChannelTreeNode

    @property
    def node_channel(self) -> str:
        """Return the channel of the node as a string."""
        return 'IOPins'

    @property
    def node_name(self) -> str:
        """Return the channel name of the node as a string."""
        return 'i'

    @property
    def children(self):
        """Return a dict of the child ChannelTreeNodes keyed by prefixes."""
        return {
            self.analog.node_name: self.analog,
            self.digital.node_name: self.digital
        }

    # Implement ChannelHandlerTreeNode

    async def on_any_message(self, message):
        """Handle any message whether or not it is recognized as by the node."""
        if message.payload is None:
            return
        self.on_response(message.channel)
