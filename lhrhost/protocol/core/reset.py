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
    """Interface for a class which receives Reset events."""

    @abstractmethod
    async def on_reset(self) -> None:
        """Receive and handle a Reset response."""
        pass


# Type-checking names
_ResetReceivers = Iterable[ResetReceiver]


# Printing

class ResetPrinter(ResetReceiver, Printer):
    """Simple class which prints received Reset responses."""

    async def on_reset(self) -> None:
        """Receive and handle a reset response."""
        self.print('Resetting')


class ResetProtocol(MessageReceiver, CommandIssuer):
    """Sends and receives hard resets."""

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

    async def notify_reset_receivers(self) -> None:
        """Notify all receivers of received Reset response."""
        for receiver in self.__reset_receivers:
            await receiver.on_reset()

    # Commands

    async def request_reset(self):
        """Send a Reset command to message receivers."""
        logger.info('Resetting connection...')
        message = Message('r', 1)
        await self.issue_command(Command(message))
        logger.debug('Reset command acknowledged!')

    async def request_complete_reset(self):
        """Send a Reset command to message receivers."""
        logger.info('Resetting connection...')
        message = Message('r', 1)
        await self.issue_command(Command(
            message, additional_events=[self.connection_synchronizer.disconnected]
        ))
        logger.debug('Reset command acknowledged, connection lost!')
        await self.connection_synchronizer.connected.wait()
        logger.debug('Connection fully reset!')

    # Implement MessageReceiver

    async def on_message(self, message: Message) -> None:
        """Handle received message.

        Only handles known Reset messages.
        """
        if message.payload is None:
            return
        if message.channel == 'r' and message.payload == 1:
            await self.notify_reset_receivers()
        self.on_response(message.channel)
