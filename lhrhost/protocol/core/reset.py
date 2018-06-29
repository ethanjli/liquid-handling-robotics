"""Reset channels of core protocol."""

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


# Receipt of Resets

class Receiver(object, metaclass=InterfaceClass):
    """Interface for a class which receives Reset events."""

    @abstractmethod
    async def on_reset(self) -> None:
        """Receive and handle a Reset response."""
        pass


# Type-checking names
_Receivers = Iterable[Receiver]


# Printing

class Printer(Receiver, Printer):
    """Simple class which prints received Reset responses."""

    async def on_reset(self) -> None:
        """Receive and handle a reset response."""
        self.print('Resetting')


class Protocol(ProtocolHandlerNode):
    """Sends and receives hard resets."""

    def __init__(
        self, connection_synchronizer,
        response_receivers: Optional[_Receivers]=None, **kwargs
    ):
        """Initialize member variables."""
        super().__init__('Reset', 'r', **kwargs)
        self.connection_synchronizer = connection_synchronizer
        self.response_receivers: List[Receiver] = []
        if response_receivers:
            self.response_receivers = [receiver for receiver in response_receivers]

    # Commands

    async def request(self):
        """Send a Reset command to message receivers."""
        logger.info('Resetting connection...')
        message = Message(self.name_path, 1)
        await self.issue_command(Command(message))
        logger.debug('Reset command acknowledged!')

    async def request_complete(self):
        """Send a Reset command to message receivers."""
        logger.info('Resetting connection...')
        message = Message(self.name_path, 1)
        await self.issue_command(Command(
            message, additional_events=[self.connection_synchronizer.disconnected]
        ))
        logger.debug('Reset command acknowledged, connection lost!')
        await self.connection_synchronizer.connected.wait()
        logger.debug('Connection fully reset!')

    # Implement ProtocolHandlerNode

    def transform_response_payload(self, payload):
        """Transform the payload into a list of args for the response receiver's method.

        The list of args will be unpacked in the response receiver's method, which
        is specified by get_response_notifier. Return None to avoid notifying any
        receivers.
        """
        if payload == 1:
            return ()
        elif payload == 0:
            return None
        else:
            raise ValueError('Invalid {} payload {}!'.format(
                self.channel_path, payload
            ))

    def get_response_notifier(self, receiver: Receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_reset
