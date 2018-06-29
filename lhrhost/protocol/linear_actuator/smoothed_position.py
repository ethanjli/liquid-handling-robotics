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


class SnapMultiplierProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator position smoother's snap multiplier."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('SnapMultiplier', 's', **kwargs)
        self.response_receivers = self.parent.response_receivers

    # Commands

    async def request(self, multiplier: Optional[int]=None):
        """Send a LA/SP/SnapMultiplier request command to message receivers."""
        # TODO: validate the multiplier
        message = Message(self.name_path, multiplier)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_linear_actuator_smoothed_position_snap_multiplier


class RangeLowProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator position smoother's minimum position."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('RangeLow', 'l', **kwargs)
        self.response_receivers = self.parent.response_receivers

    # Commands

    async def request(self, position: Optional[int]=None):
        """Send a LA/SP/RangeLow request command to message receivers."""
        # TODO: validate the multiplier
        message = Message(self.name_path, position)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_linear_actuator_smoothed_position_range_low


class RangeHighProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator position smoother's minimum position."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('RangeHigh', 'h', **kwargs)
        self.response_receivers = self.parent.response_receivers

    # Commands

    async def request(self, position: Optional[int]=None):
        """Send a LA/SP/RangeHigh request command to message receivers."""
        # TODO: validate the multiplier
        message = Message(self.name_path, position)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_linear_actuator_smoothed_position_range_high


class ActivityThresholdProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator position smoother's minimum position."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('ActivityThreshold', 't', **kwargs)
        self.response_receivers = self.parent.response_receivers

    # Commands

    async def request(self, position_difference: Optional[int]=None):
        """Send a LA/SP/ActivityThreshold request command to message receivers."""
        # TODO: validate the multiplier
        message = Message(self.name_path, position_difference)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_linear_actuator_smoothed_position_activity_threshold


class Protocol(ProtocolHandlerNode):
    """Notifies on the linear actuator's position."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('SmoothedPosition', 's', **kwargs)
        self.response_receivers = self.parent.response_receivers

        self.notify = NotifyProtocol(parent=self)
        self.snap_multiplier = SnapMultiplierProtocol(parent=self)
        self.range_low = RangeLowProtocol(parent=self)
        self.range_high = RangeHighProtocol(parent=self)
        self.activity_threshold = ActivityThresholdProtocol(parent=self)

    async def notify_response_receivers(self, position: int) -> None:
        """Notify all receivers of received LA/SmoothedPosition response."""
        for receiver in self.response_receivers:
            await receiver.on_linear_actuator_smoothed_position(position)

    # Commands

    async def request(self):
        """Send a LA/SmoothedPosition request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    @property
    def children_list(self):
        """Return a list of child nodes."""
        return [
            self.notify,
            self.snap_multiplier,
            self.range_low, self.range_high,
            self.activity_threshold
        ]
