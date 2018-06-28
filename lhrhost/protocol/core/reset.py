"""Reset channels of core protocol."""

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


# Receipt of Resets

class ResetReceiver(object, metaclass=InterfaceClass):
    """Interface for a class which receives reset events.

    This may include versions from self or from other sources.
    """

    @abstractmethod
    def on_reset(self) -> None:
        """Receive and handle a reset."""
        pass


# Type-checking names
_ResetReceivers = Iterable[ResetReceiver]


# Printing

class ResetPrinter(ResetReceiver, Printer):
    """Simple class which prints received serialized messages."""

    def on_reset(self) -> None:
        """Receive and handle a reset response."""
        self.print('Resetting')


class ResetProtocol(MessageReceiver, CommandIssuer):
    """Determines and prints protocol version."""

    def __init__(
        self, connection_synchronizer,
        reset_receivers: Optional[_ResetReceivers]=None, **kwargs
    ):
        """Initialize member variables."""
        super().__init__(**kwargs)
        self.connection_synchronizer = connection_synchronizer
        self.__reset_receivers: List[ResetReceiver] = []
        if reset_receivers:
            self.__reset_receivers = [receiver for receiver in reset_receivers]

    def notify_reset_receivers(self) -> None:
        """Notify all receivers of impending reset."""
        for receiver in self.__reset_receivers:
            receiver.on_reset()

    # Commands

    async def request_reset(self):
        """Send a reset request command to message receivers."""
        logger.info('Resetting connection...')
        await self.notify_message_receivers(Message('r', 1))

    async def request_wait_reset(self):
        """Send a reset request command to message receivers."""
        logger.info('Resetting connection...')
        await self.issue_command(Command(Message('r', 1), ['r']))
        logger.debug('Reset command acknowledged!')

    async def request_complete_reset(self):
        """Send a reset request command to message receivers."""
        logger.info('Resetting connection...')
        await self.issue_command(Command(
            Message('r', 1), ['r'], [self.connection_synchronizer.disconnected]
        ))
        logger.debug('Reset command acknowledged, connection lost!')
        await self.connection_synchronizer.connected.wait()
        logger.debug('Connection fully reset!')

    # Implement DeserializedMessageReceiver

    async def on_message(self, message: Message) -> None:
        """Handle received message.

        Only handles known reset messages.
        """
        if message.payload is None:
            return
        if message.channel == 'r' and message.payload == 1:
            self.notify_reset_receivers()
        self.on_response(message.channel)
