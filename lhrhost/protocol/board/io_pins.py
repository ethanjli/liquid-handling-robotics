"""IOPins channels of board protocol."""

# Standard imports
import logging
from abc import abstractmethod
from typing import Iterable, List, Optional

# Local package imports
from lhrhost.messaging.presentation import Message
from lhrhost.protocol import ChannelHandlerTreeNode, Command, CommandIssuer
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


class IOPinsTypeProtocol(ChannelHandlerTreeNode, CommandIssuer):
    """Reads IO pins of the specified type."""

    def __init__(self, parent, node_channel, node_name, **kwargs):
        """Initialize member variables."""
        super().__init__(**kwargs)
        self.command_receivers = parent.command_receivers
        self.io_pins_receivers = parent.io_pins_receivers
        self._parent = parent
        self._node_channel = node_channel
        self._node_name = node_name

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

    # Implement ChannelTreeNode

    @property
    def parent(self):
        """Return the parent ChannelTreeNode."""
        return self._parent

    @property
    def node_channel(self) -> str:
        """Return the channel of the node as a string."""
        return self._node_channel

    @property
    def node_name(self) -> str:
        """Return the channel name of the node as a string."""
        return self._node_name

    # Implement ChannelHandlerTreeNode

    async def on_received_message(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the node."""
        if message.payload is None:
            return
        # TODO: validate the channel name
        await self.notify_io_pins_receivers(channel_name_remainder, message.payload)
        self.on_response(message.channel)


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

    async def on_received_message(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the node."""
        if message.payload is None:
            return
        self.on_response(message.channel)
