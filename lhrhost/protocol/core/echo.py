"""Echo channels of core protocol."""

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


# Receipt of Echoes

class Receiver(object, metaclass=InterfaceClass):
    """Interface for a class which receives Echo events."""

    @abstractmethod
    async def on_echo(self, payload: int) -> None:
        """Receive and handle a Echo response."""
        pass


# Type-checking names
_Receivers = Iterable[Receiver]


# Printing

class Printer(Receiver, Printer):
    """Simple class which prints received Echo responses."""

    async def on_echo(self, payload: int) -> None:
        """Receive and handle a Echo response."""
        self.print('Echo: {}'.format(payload))


class Protocol(ProtocolHandlerNode):
    """Sends and receives echoes."""

    def __init__(
        self, response_receivers: Optional[_Receivers]=None, **kwargs
    ):
        """Initialize member variables."""
        super().__init__('Echo', 'e', **kwargs)
        self.response_receivers: List[Receiver] = []
        if response_receivers:
            self.response_receivers = [receiver for receiver in response_receivers]

    # Commands

    async def request(self, payload: Optional[int]=None):
        """Send a Echo command to message receivers."""
        message = Message(self.name_path, payload)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver: Receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_echo
