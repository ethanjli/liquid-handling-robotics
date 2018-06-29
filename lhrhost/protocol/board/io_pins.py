"""IOPins channels of board protocol."""

# Standard imports
import logging
from abc import abstractmethod
from typing import Iterable, List, Optional

# Local package imports
from lhrhost.messaging.presentation import Message
from lhrhost.protocol import Command, ProtocolHandlerNode
from lhrhost.util.interfaces import InterfaceClass
from lhrhost.util.printing import Printer

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# Receipt of IOPins

class Receiver(object, metaclass=InterfaceClass):
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
_Receivers = Iterable[Receiver]


# Printing

class Printer(Receiver, Printer):
    """Simple class which prints received IOPins/* responses."""

    async def on_io_pin_digital(self, pin: int, payload: int) -> None:
        """Receive and handle a IOPins/Digital/* response."""
        self.print('Pin {}: {}'.format(
            pin, 'HIGH' if payload else 'LOW'
        ))

    async def on_io_pin_analog(self, pin: int, payload: int) -> None:
        """Receive and handle an IOPins/Analog/* response."""
        self.print('Pin A{}: {}'.format(pin, payload))


class TypeProtocol(ProtocolHandlerNode):
    """Reads IO pins of the specified type."""

    def __init__(self, channel, channel_name, **kwargs):
        """Initialize member variables."""
        super().__init__(channel, channel_name, **kwargs)
        self.response_receivers = self.parent.response_receivers

    async def notify_response_receivers(self, pin: int, payload: int) -> None:
        """Notify all receivers of received IOPins/_/_ response."""
        for receiver in self.response_receivers:
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

    async def on_received_message(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the node."""
        if message.payload is None:
            return
        await self.notify_response_receivers(channel_name_remainder, message.payload)


class Protocol(ProtocolHandlerNode):
    """Reads digital and analog IO pins."""

    def __init__(
        self, response_receivers: Optional[_Receivers]=None, **kwargs
    ):
        """Initialize member variables."""
        super().__init__('IOPins', 'i', **kwargs)

        self.response_receivers: List[Receiver] = []
        if response_receivers:
            self.response_receivers = [receiver for receiver in response_receivers]

        self.analog = TypeProtocol('Analog', 'a', parent=self, **kwargs)
        self.digital = TypeProtocol('Digital', 'd', parent=self, **kwargs)

    # Implement ProtocolHandlerNode

    @property
    def children_list(self):
        """Return a list of child nodes."""
        return [self.analog, self.digital]
