"""LinearActuator channels of linear actuator protocol."""

# Standard imports
import logging
from typing import Optional

# Local package imports
from lhrhost.messaging.presentation import Message
from lhrhost.protocol import Command, ProtocolHandlerNode

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class IntervalProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator signal notifier's notification interval."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('Interval', 'i', **kwargs)
        self.response_receivers = self.parent.response_receivers

    # Commands

    async def request(self, interval: Optional[int]=None):
        """Send a LA/_/Notify/Interval request command to message receivers."""
        # TODO: validate the timeout
        message = Message(self.name_path, interval)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        if self.parent.parent.node_channel == 'Position':
            return receiver.on_linear_actuator_position_notify_interval
        elif self.parent.parent.node_channel == 'SmoothedPosition':
            return receiver.on_linear_actuator_smoothed_position_notify_interval
        elif self.parent.parent.node_channel == 'Motor':
            return receiver.on_linear_actuator_motor_notify_interval
        else:
            logger.error(
                'Notifications not implemented for parent {}!'
                .format(self.parent.parent.node_channel)
            )
            return None


class ChangeOnlyProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator signal notifier's notification behavior."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('ChangeOnly', 'c', **kwargs)
        self.response_receivers = self.parent.response_receivers

    # Commands

    async def request(self, state: Optional[int]=None):
        """Send a LA/_/Notify/ChangeOnly request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path, state)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        if self.parent.parent.node_channel == 'Position':
            return receiver.on_linear_actuator_position_notify_change_only
        elif self.parent.parent.node_channel == 'SmoothedPosition':
            return receiver.on_linear_actuator_smoothed_position_notify_change_only
        elif self.parent.parent.node_channel == 'Motor':
            return receiver.on_linear_actuator_motor_notify_change_only
        else:
            logger.error(
                'Notifications not implemented for parent {}!'
                .format(self.parent.parent.node_channel)
            )
            return None


class NumberProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator signal notifier's notification duration."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('Number', 'n', **kwargs)
        self.response_receivers = self.parent.response_receivers

    # Commands

    async def request(self, number: Optional[int]=None):
        """Send a LA/_/Notify/Number request command to message receivers."""
        # TODO: validate the number
        message = Message(self.name_path, number)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        if self.parent.parent.node_channel == 'Position':
            return receiver.on_linear_actuator_position_notify_number
        elif self.parent.parent.node_channel == 'SmoothedPosition':
            return receiver.on_linear_actuator_smoothed_position_notify_number
        elif self.parent.parent.node_channel == 'Motor':
            return receiver.on_linear_actuator_motor_notify_number
        else:
            logger.error(
                'Notifications not implemented for parent {}!'
                .format(self.parent.parent.node_channel)
            )
            return None


class Protocol(ProtocolHandlerNode):
    """Notifies on the parent's value."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('Notify', 'n', **kwargs)
        self.response_receivers = self.parent.response_receivers

        self.interval = IntervalProtocol(parent=self)
        self.change_only = ChangeOnlyProtocol(parent=self)
        self.number = NumberProtocol(parent=self)

    # Commands

    async def request(self, state: Optional[int]=None):
        """Send a LA/_/Notify request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path, state)
        await self.issue_command(Command(message))

    async def request_complete_time_interval(self, number: int, time_interval: int):
        """Send a LA/_/Notify request command to message receivers.

        Receives a finite number of notifications.
        """
        message = Message(self.name_path, 2)
        wait_channels = [self.name_path, self.number.name_path, self.name_path]
        await self.number.request(number)
        await self.interval.request(time_interval)
        logger.debug('Starting to notify on {}...'.format(self.parent.channel_path))
        await self.issue_command(Command(message, wait_channels))
        logger.debug('Finished notifying on {}!'.format(self.parent.channel_path))

    async def request_complete_iterations_interval(self, number: int, iterations_interval: int):
        """Send a LA/_Notify request command to message receivers.

        Receives a finite number of notifications.
        """
        message = Message(self.name_path, 1)
        wait_channels = [self.name_path, self.number.name_path, self.name_path]
        await self.number.request(number)
        await self.interval.request(iterations_interval)
        logger.debug('Starting to notify on {}...'.format(self.parent.channel_path))
        await self.issue_command(Command(message, wait_channels))
        logger.debug('Finished notifying on {}...'.format(self.parent.channel_path))

    # Implement ProtocolHandlerNode

    @property
    def children_list(self):
        """Return a list of child nodes."""
        return [self.interval, self.change_only, self.number]

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        if self.parent.node_channel == 'Position':
            return receiver.on_linear_actuator_position_notify
        elif self.parent.node_channel == 'SmoothedPosition':
            return receiver.on_linear_actuator_smoothed_position_notify
        elif self.parent.node_channel == 'Motor':
            return receiver.on_linear_actuator_motor_notify
        else:
            logger.error(
                'Notifications not implemented for parent {}!'
                .format(self.parent.node_channel)
            )
            return None
