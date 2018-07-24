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


class LimitsPositionLimitProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator feedback controller's PID coefficient."""

    def __init__(self, channel, channel_name, **kwargs):
        """Initialize member variables."""
        super().__init__(channel, channel_name, **kwargs)
        self.response_receivers = self.parent.response_receivers

    # Commands

    async def request(self, position: Optional[int]=None):
        """Send a LA/FC/Limits/Position/_ request command to message receivers."""
        # TODO: validate the position
        message = Message(self.name_path, position)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        if self.node_channel == 'Low':
            return receiver.on_linear_actuator_feedback_controller_limits_position_low
        elif self.node_channel == 'High':
            return receiver.on_linear_actuator_feedback_controller_limits_position_high
        else:
            logger.error(
                'Position limit type {} not implemented!'
                .format(self.node_channel)
            )
            return None


class LimitsPositionProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator feedback controller's position limits."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('Position', 'p', **kwargs)
        self.response_receivers = self.parent.response_receivers

        self.low = LimitsPositionLimitProtocol('Low', 'l', parent=self)
        self.high = LimitsPositionLimitProtocol('High', 'h', parent=self)

    # Implement ProtocolHandlerNode

    @property
    def children_list(self):
        """Return a list of child nodes."""
        return [self.low, self.high]


class LimitsMotorLimitProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator feedback controller's PID coefficient."""

    def __init__(self, channel, channel_name, **kwargs):
        """Initialize member variables."""
        super().__init__(channel, channel_name, **kwargs)
        self.response_receivers = self.parent.response_receivers

    # Commands

    async def request(self, position: Optional[int]=None):
        """Send a LA/FC/Limits/Motor/_/_ request command to message receivers."""
        # TODO: validate the position
        message = Message(self.name_path, position)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        if self.node_channel == 'Low':
            if self.parent.node_channel == 'Forwards':
                return receiver.on_linear_actuator_feedback_controller_limits_motor_forwards_low
            if self.parent.node_channel == 'Backwards':
                return receiver.on_linear_actuator_feedback_controller_limits_motor_backwards_low
            else:
                logger.error(
                    'Motor direction type {} not implemented!'
                    .format(self.node_channel)
                )
                return None
        elif self.node_channel == 'High':
            if self.parent.node_channel == 'Forwards':
                return receiver.on_linear_actuator_feedback_controller_limits_motor_forwards_high
            if self.parent.node_channel == 'Backwards':
                return receiver.on_linear_actuator_feedback_controller_limits_motor_backwards_high
            else:
                logger.error(
                    'Motor direction type {} not implemented!'
                    .format(self.node_channel)
                )
                return None
        else:
            logger.error(
                'Motor limit type {} not implemented!'
                .format(self.node_channel)
            )
            return None


class LimitsMotorDirectionProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator feedback controller's motor duty direction limits."""

    def __init__(self, channel, channel_name, **kwargs):
        """Initialize member variables."""
        super().__init__(channel, channel_name, **kwargs)
        self.response_receivers = self.parent.response_receivers

        self.low = LimitsMotorLimitProtocol('Low', 'l', parent=self)
        self.high = LimitsMotorLimitProtocol('High', 'h', parent=self)

    # Implement ProtocolHandlerNode

    @property
    def children_list(self):
        """Return a list of child nodes."""
        return [self.low, self.high]


class LimitsMotorProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator feedback controller's motor duty limits."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('Motor', 'm', **kwargs)
        self.response_receivers = self.parent.response_receivers

        self.forwards = LimitsMotorDirectionProtocol('Forwards', 'f', parent=self)
        self.backwards = LimitsMotorDirectionProtocol('Backwards', 'b', parent=self)

    # Implement ProtocolHandlerNode

    @property
    def children_list(self):
        """Return a list of child nodes."""
        return [self.forwards, self.backwards]


class LimitsProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator feedback controller's limits."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('Limits', 'l', **kwargs)
        self.response_receivers = self.parent.response_receivers

        self.position = LimitsPositionProtocol(parent=self)
        self.motor = LimitsMotorProtocol(parent=self)

    # Implement ProtocolHandlerNode

    @property
    def children_list(self):
        """Return a list of child nodes."""
        return [self.position, self.motor]


class PIDCoefficientProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator feedback controller's PID coefficient."""

    def __init__(self, channel, channel_name, **kwargs):
        """Initialize member variables."""
        super().__init__(channel, channel_name, **kwargs)
        self.response_receivers = self.parent.response_receivers

    # Commands

    async def request(self, coefficient: Optional[int]=None):
        """Send a LA/FC/PID/_ request command to message receivers."""
        # TODO: validate the coefficient
        message = Message(self.name_path, coefficient)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        if self.node_channel == 'Kp':
            return receiver.on_linear_actuator_feedback_controller_pid_kp
        elif self.node_channel == 'Kd':
            return receiver.on_linear_actuator_feedback_controller_pid_kd
        elif self.node_channel == 'Ki':
            return receiver.on_linear_actuator_feedback_controller_pid_ki
        else:
            logger.error(
                'PID coefficient type {} not implemented!'
                .format(self.node_channel)
            )
            return None


class SampleIntervalProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator feedback controller's PID sample interval."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('SampleInterval', 's', **kwargs)
        self.response_receivers = self.parent.response_receivers

    # Commands

    async def request(self, interval: Optional[int]=None):
        """Send a LA/FC/SampleInterval request command to message receivers."""
        # TODO: validate the interval
        message = Message(self.name_path, interval)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_linear_actuator_feedback_controller_pid_sample_interval


class PIDProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator feedback controller's PID parameters."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('PID', 'p', **kwargs)
        self.response_receivers = self.parent.response_receivers
        self.kp = PIDCoefficientProtocol('Kp', 'p', parent=self)
        self.kd = PIDCoefficientProtocol('Kd', 'd', parent=self)
        self.ki = PIDCoefficientProtocol('Ki', 'i', parent=self)
        self.sample_interval = SampleIntervalProtocol(parent=self)

    # Implement ProtocolHandlerNode

    @property
    def children_list(self):
        """Return a list of child nodes."""
        return [self.kp, self.kd, self.ki, self.sample_interval]


class ConvergenceTimeoutProtocol(ProtocolHandlerNode):
    """Notifies on the linear actuator feedback controller's convergence detector timeout."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('ConvergenceTimeout', 'c', **kwargs)
        self.response_receivers = self.parent.response_receivers

    # Commands

    async def request(self, timeout: Optional[int]=None):
        """Send a LA/FC/ConvergenceTimeout request command to message receivers."""
        # TODO: validate the timeout
        message = Message(self.name_path, timeout)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_linear_actuator_feedback_controller_convergence_timeout


class Protocol(ProtocolHandlerNode):
    """Notifies on the linear actuator feedback controller's state."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('FeedbackController', 'f', **kwargs)
        self.response_receivers = self.parent.response_receivers

        self.limits = LimitsProtocol(parent=self)
        self.pid = PIDProtocol(parent=self)
        self.convergence_timeout = ConvergenceTimeoutProtocol(parent=self)

    # Commands

    async def request(self, position: Optional[int]=None):
        """Send a LA/FC request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path, position)
        await self.issue_command(Command(message))

    async def request_complete(self, position: Optional[int]=None):
        """Send a LA/FC request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path, position)
        wait_channels = [
            # Initial responses
            self.name_path,
            self.parent.name_path,
            # Responses after actuator stops
            self.parent.position.name_path,
            self.name_path,
            self.parent.name_path
        ]
        logger.debug('Starting feedback control...')
        await self.issue_command(Command(message, wait_channels))
        logger.debug('Finished feedback control!')

    # Implement ProtocolHandlerNode

    @property
    def children_list(self):
        """Return a list of child nodes."""
        return [self.limits, self.pid, self.convergence_timeout]

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_linear_actuator_feedback_controller
