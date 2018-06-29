"""LinearActuator channels of linear actuator protocol."""

# Standard imports
import logging
from typing import Optional

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
        super().__init__('SmoothedPosition', 's', **kwargs)
        self.command_receivers = self.parent.command_receivers
        self.response_receivers = self.parent.response_receivers

        self.notify = NotifyProtocol(parent=self)

    async def notify_response_receivers(self, position: int) -> None:
        """Notify all receivers of received LA/SmoothedPosition response."""
        for receiver in self.response_receivers:
            await receiver.on_linear_actuator_smoothed_position(position)

    async def notify_response_receivers_snap_multiplier(
        self, multiplier: int
    ) -> None:
        """Notify all receivers of received LA/SP/SnapMultiplier response."""
        for receiver in self.response_receivers:
            await receiver.on_linear_actuator_smoothed_position_snap_multiplier(
                multiplier
            )

    async def notify_response_receivers_range_low(
        self, position: int
    ) -> None:
        """Notify all receivers of received LA/SP/RangeLow response."""
        for receiver in self.response_receivers:
            await receiver.on_linear_actuator_smoothed_position_range_low(
                position
            )

    async def notify_response_receivers_range_high(
        self, position: int
    ) -> None:
        """Notify all receivers of received LA/SP/RangeHigh response."""
        for receiver in self.response_receivers:
            await receiver.on_linear_actuator_smoothed_position_range_high(
                position
            )

    async def notify_response_receivers_activity_threshold(
        self, position_difference: int
    ) -> None:
        """Notify all receivers of received LA/SP/ActivityThreshold response."""
        for receiver in self.response_receivers:
            await receiver.on_linear_actuator_smoothed_position_activity_threshold(
                position_difference
            )

    # Commands

    async def request(self):
        """Send a LA/SmoothedPosition request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path)
        await self.issue_command(Command(message))

    async def request_snap_multiplier(self, multiplier: Optional[int]=None):
        """Send a LA/SP/SnapMultiplier request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path + 's', multiplier)
        await self.issue_command(Command(message))

    async def request_range_low(self, position: Optional[int]=None):
        """Send a LA/SP/RangeLow request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path + 'l', position)
        await self.issue_command(Command(message))

    async def request_range_high(self, position: Optional[int]=None):
        """Send a LA/SP/RangeHigh request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path + 'h', position)
        await self.issue_command(Command(message))

    async def request_activity_threshold(self, position_difference: Optional[int]=None):
        """Send a LA/SP/ActivityThreshold request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path + 't', position_difference)
        await self.issue_command(Command(message))

    # Implement ChannelHandlerTreeNode

    @property
    def children(self):
        """Return a dict of handlers, keyed by channel paths below current path."""
        return {
            self.notify.node_name: self.notify
        }

    @property
    def child_handlers(self):
        """Return a dict of handlers, keyed by channel paths below current path."""
        return {
            's': self.on_received_message_snap_multiplier,
            'l': self.on_received_message_range_low,
            'h': self.on_received_message_range_high,
            't': self.on_received_message_activity_threshold
        }

    async def on_received_message_snap_multiplier(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_response_receivers_snap_multiplier(message.payload)

    async def on_received_message_range_low(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_response_receivers_range_low(message.payload)

    async def on_received_message_range_high(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_response_receivers_range_high(message.payload)

    async def on_received_message_activity_threshold(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_response_receivers_activity_threshold(message.payload)
