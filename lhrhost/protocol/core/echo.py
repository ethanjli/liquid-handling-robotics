"""Echo channels of core protocol."""

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


# Receipt of Echoes

class EchoReceiver(object, metaclass=InterfaceClass):
    """Interface for a class which receives Echo events."""

    @abstractmethod
    async def on_echo(self, payload: int) -> None:
        """Receive and handle a Echo response."""
        pass


# Type-checking names
_EchoReceivers = Iterable[EchoReceiver]


# Printing

class EchoPrinter(EchoReceiver, Printer):
    """Simple class which prints received Echo responses."""

    async def on_echo(self, payload: int) -> None:
        """Receive and handle a Echo response."""
        self.print('Echo: {}'.format(payload))


class EchoProtocol(ChannelHandlerTreeNode, CommandIssuer):
    """Sends and receives echoes."""

    def __init__(
        self, echo_receivers: Optional[_EchoReceivers]=None, **kwargs
    ):
        """Initialize member variables."""
        super().__init__(**kwargs)
        self.__echo_receivers: List[EchoReceiver] = []
        if echo_receivers:
            self.__echo_receivers = [receiver for receiver in echo_receivers]

    async def notify_echo_receivers(self, payload: int) -> None:
        """Notify all receivers of a received Echo response."""
        for receiver in self.__echo_receivers:
            await receiver.on_echo(payload)

    # Commands

    async def request_echo(self, payload: Optional[int]=None):
        """Send a Echo command to message receivers."""
        message = Message(self.name_path, payload)
        await self.issue_command(Command(message))

    # Implement ChannelTreeNode

    @property
    def node_channel(self) -> str:
        """Return the channel of the node as a string."""
        return 'Echo'

    @property
    def node_name(self) -> str:
        """Return the channel name of the node as a string."""
        return 'e'

    # Implement ChannelHandlerTreeNode

    async def on_received_message(self, channel_name_remainder, message) -> None:
        """Handle received message.

        Only handles known Echo messages.
        """
        if message.payload is None:
            return
        if message.channel == self.name_path:
            await self.notify_echo_receivers(message.payload)
        self.on_response(message.channel)
