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


class StallProtectorTimeoutProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator motor's stall protector timeout."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('StallProtectorTimeout', 's', **kwargs)
        self.response_receivers = self.parent.response_receivers

    # Commands

    async def request(self, timeout: Optional[int]=None):
        """Send a LA/Motor/StallProtectorTimeout request command to message receivers."""
        # TODO: validate the timeout
        message = Message(self.name_path, timeout)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_linear_actuator_motor_stall_protector_timeout


class TimerTimeoutProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator motor's stall protector timeout."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('TimerTimeout', 't', **kwargs)
        self.response_receivers = self.parent.response_receivers

    # Commands

    async def request(self, timeout: Optional[int]=None):
        """Send a LA/Motor/TimerTimeout request command to message receivers."""
        # TODO: validate the timeout
        message = Message(self.name_path, timeout)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_linear_actuator_motor_timer_timeout


class MotorPolarityProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator motor's polarity."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('MotorPolarity', 'p', **kwargs)
        self.response_receivers = self.parent.response_receivers

    # Commands

    async def request(self, state: Optional[int]=None):
        """Send a LA/Motor/MotorPolarity request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path, state)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_linear_actuator_motor_motor_polarity


class Protocol(ProtocolHandlerNode):
    """Notifies on the linear actuator's motor duty."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('Motor', 'm', **kwargs)
        self.response_receivers = self.parent.response_receivers

        self.notify = NotifyProtocol(parent=self)
        self.stall_protector_timeout = StallProtectorTimeoutProtocol(parent=self)
        self.timer_timeout = TimerTimeoutProtocol(parent=self)
        self.motor_polarity = MotorPolarityProtocol(parent=self)

    # Commands

    async def request(self, duty: Optional[int]=None):
        """Send a LA/Motor request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path, duty)
        await self.issue_command(Command(message))

    async def request_complete(self, duty: Optional[int]=None):
        """Send a LA/Motor request command to message receivers."""
        # TODO: validate the state
        if duty == 0:
            await self.request(0)
            return
        message = Message(self.name_path, duty)
        wait_channels = [
            # Initial responses
            self.name_path,
            self.parent.name_path,
            # Responses after actuator stops
            self.parent.position.name_path,
            self.name_path,
            self.parent.name_path
        ]
        logger.debug('Starting motor direct duty control...')
        await self.issue_command(Command(message, wait_channels))
        logger.debug('Finished motor direct duty control!')

    # Implement ProtocolHandlerNode

    @property
    def children_list(self):
        """Return a list of child nodes."""
        return [
            self.notify,
            self.stall_protector_timeout, self.timer_timeout, self.motor_polarity
        ]

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_linear_actuator_motor
