"""LinearActuator channels of linear actuator protocol."""

# Standard imports
import asyncio
import logging

# Local package imports
from lhrhost.messaging.presentation import Message
from lhrhost.protocol import Command, ProtocolHandlerNode
from lhrhost.protocol.linear_actuator.notify import Protocol as NotifyProtocol

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Protocol(ProtocolHandlerNode):
    """Notifies on the linear actuator's position."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('Position', 'p', **kwargs)
        self.response_receivers = self.parent.response_receivers

        self.notify = NotifyProtocol(parent=self)

    async def notify_response_receivers(self, position: int) -> None:
        """Notify all receivers of received LA/Position response."""
        await asyncio.gather(*[
            receiver.on_linear_actuator_position(position)
            for receiver in self.response_receivers
        ])

    # Commands

    async def request(self):
        """Send a LA/Position request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    @property
    def children_list(self):
        """Return a list of child nodes."""
        return [self.notify]
