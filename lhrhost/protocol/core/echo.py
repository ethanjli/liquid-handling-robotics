"""Echo channels of core protocol."""

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


# Receipt of Echoes

class EchoReceiver(object, metaclass=InterfaceClass):
    """Interface for a class which receives echo events.

    This may include versions from self or from other sources.
    """

    @abstractmethod
    def on_echo(self, payload: int) -> None:
        """Receive and handle a echo."""
        pass


# Type-checking names
_EchoReceivers = Iterable[EchoReceiver]


# Printing

class EchoPrinter(EchoReceiver, Printer):
    """Simple class which prints received serialized messages."""

    def on_echo(self, payload: int) -> None:
        """Receive and handle a serialized message."""
        self.print('Echo {}'.format(payload))


class EchoProtocol(MessageReceiver, CommandIssuer):
    """Determines and prints protocol version."""

    def __init__(
        self, echo_receivers: Optional[_EchoReceivers]=None, **kwargs
    ):
        """Initialize member variables."""
        super().__init__(**kwargs)
        self.__echo_receivers: List[EchoReceiver] = []
        if echo_receivers:
            self.__echo_receivers = [receiver for receiver in echo_receivers]

    def notify_echo_receivers(self, payload: int) -> None:
        """Notify all receivers of impending echo."""
        for receiver in self.__echo_receivers:
            receiver.on_echo(payload)

    # Commands

    async def request_echo(self, payload: int):
        """Send an echo request command to message receivers."""
        await self.notify_message_receivers(Message('e', payload))

    async def request_wait_echo(self, payload: int):
        """Send an echo request command to message receivers."""
        await self.issue_command(
            Command(Message('e', payload), ['e'])
        )

    # Implement DeserializedMessageReceiver

    async def on_message(self, message: Message) -> None:
        """Handle received message.

        Only handles known echo messages.
        """
        if message.payload is None:
            return
        if message.channel == 'e':
            self.notify_echo_receivers(message.payload)
        self.on_response(message.channel)
