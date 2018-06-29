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


class Protocol(ProtocolHandlerNode):
    """Notifies on the parent's value."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('Notify', 'n', **kwargs)
        self.command_receivers = self.parent.command_receivers
        self.response_receivers = self.parent.response_receivers

    async def notify_response_receivers(self, state: int) -> None:
        """Notify all receivers of received LA/_/Notify response."""
        for receiver in self.response_receivers:
            if self.parent.node_channel == 'Position':
                await receiver.on_linear_actuator_position_notify(state)
            elif self.parent.node_channel == 'SmoothedPosition':
                await receiver.on_linear_actuator_smoothed_position_notify(state)
            elif self.parent.node_channel == 'Motor':
                await receiver.on_linear_actuator_motor_notify(state)
            else:
                raise NotImplementedError(
                    'Notifications not supported for parent {}!'
                    .format(self.parent.node_channel)
                )

    async def notify_response_receivers_interval(self, interval: int) -> None:
        """Notify all receivers of received LA/_/Notify/Interval response."""
        for receiver in self.response_receivers:
            if self.parent.node_channel == 'Position':
                await receiver.on_linear_actuator_position_notify_interval(interval)
            elif self.parent.node_channel == 'SmoothedPosition':
                await receiver.on_linear_actuator_smoothed_position_notify_interval(interval)
            elif self.parent.node_channel == 'Motor':
                await receiver.on_linear_actuator_motor_notify_interval(interval)
            else:
                raise NotImplementedError(
                    'Notifications not supported for parent {}!'
                    .format(self.parent.node_channel)
                )

    async def notify_response_receivers_change_only(self, state: int) -> None:
        """Notify all receivers of received LA/_/Notify/ChangeOnly response."""
        for receiver in self.response_receivers:
            if self.parent.node_channel == 'Position':
                await receiver.on_linear_actuator_position_notify_change_only(state)
            elif self.parent.node_channel == 'SmoothedPosition':
                await receiver.on_linear_actuator_smoothed_position_notify_change_only(state)
            elif self.parent.node_channel == 'Motor':
                await receiver.on_linear_actuator_motor_notify_change_only(state)
            else:
                raise NotImplementedError(
                    'Notifications not supported for parent {}!'
                    .format(self.parent.node_channel)
                )

    async def notify_response_receivers_number(self, number: int) -> None:
        """Notify all receivers of received LA/_/Notify/number response."""
        for receiver in self.response_receivers:
            if self.parent.node_channel == 'Position':
                await receiver.on_linear_actuator_position_notify_number(number)
            elif self.parent.node_channel == 'SmoothedPosition':
                await receiver.on_linear_actuator_smoothed_position_notify_number(number)
            elif self.parent.node_channel == 'Motor':
                await receiver.on_linear_actuator_motor_notify_number(number)
            else:
                raise NotImplementedError(
                    'Notifications not supported for parent {}!'
                    .format(self.parent.node_channel)
                )

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
        wait_channels = [self.name_path, self.name_path + 'n', self.name_path]
        await self.request_number(number)
        await self.request_interval(time_interval)
        logger.debug('Starting to notify on {}...'.format(self.parent.channel_path))
        await self.issue_command(Command(message, wait_channels))
        logger.debug('Finished notifying on {}!'.format(self.parent.channel_path))

    async def request_complete_iterations_interval(self, number: int, iterations_interval: int):
        """Send a LA/_Notify request command to message receivers.

        Receives a finite number of notifications.
        """
        message = Message(self.name_path, 1)
        wait_channels = [self.name_path, self.name_path + 'n', self.name_path]
        await self.request_number(number)
        await self.request_interval(iterations_interval)
        logger.debug('Starting to notify on {}...'.format(self.parent.channel_path))
        await self.issue_command(Command(message, wait_channels))
        logger.debug('Finished notifying on {}...'.format(self.parent.channel_path))

    async def request_interval(self, interval: Optional[int]=None):
        """Send a LinearActuator/Blink/HighInterval request command to message receivers."""
        # TODO: validate the interval
        message = Message(self.name_path + 'i', interval)
        await self.issue_command(Command(message))

    async def request_change_only(self, state: Optional[int]=None):
        """Send a LinearActuator/Blink/Notify request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path + 'c', state)
        await self.issue_command(Command(message))

    async def request_number(self, number: Optional[int]=None):
        """Send a LinearActuator/Blink/Periods request command to message receivers."""
        # TODO: validate the number
        message = Message(self.name_path + 'n', number)
        await self.issue_command(Command(message))

    # Implement ChannelHandlerTreeNode

    @property
    def child_handlers(self):
        """Return a dict of handlers, keyed by channel paths below current path."""
        return {
            'i': self.on_received_message_interval,
            'c': self.on_received_message_change_only,
            'n': self.on_received_message_number
        }

    async def on_received_message_interval(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_response_receivers_interval(message.payload)

    async def on_received_message_change_only(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_response_receivers_change_only(message.payload)

    async def on_received_message_number(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_response_receivers_number(message.payload)
