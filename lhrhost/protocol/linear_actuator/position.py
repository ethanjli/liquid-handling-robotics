"""LinearActuator channels of linear actuator protocol."""

# Standard imports
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
        self.command_receivers = self.parent.command_receivers
        self.response_receivers = self.parent.response_receivers

        self.notify = NotifyProtocol(parent=self)

    async def notify_response_receivers(self, position: int) -> None:
        """Notify all receivers of received LA/Position response."""
        for receiver in self.response_receivers:
            await receiver.on_linear_actuator_position(position)

    # Commands

    async def request(self):
        """Send a LA/Position request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path)
        await self.issue_command(Command(message))

    # Implement ChannelHandlerTreeNode

    @property
    def children(self):
        """Return a dict of handlers, keyed by channel paths below current path."""
        return {
            self.notify.node_name: self.notify
        }
