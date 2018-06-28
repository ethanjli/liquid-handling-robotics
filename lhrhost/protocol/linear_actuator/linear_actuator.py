"""LinearActuator channels of linear actuator protocol."""

# Standard imports
import logging
from abc import abstractmethod
from typing import Iterable, List, Optional

# Local package imports
from lhrhost.messaging.presentation import Message
from lhrhost.protocol import (
    ChannelHandlerTreeChildNode, ChannelHandlerTreeNode,
    Command, CommandIssuer
)
from lhrhost.util.interfaces import InterfaceClass
from lhrhost.util.printing import Printer

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# Receipt of LinearActuator

class LinearActuatorReceiver(object, metaclass=InterfaceClass):
    """Interface for a class which receives linear_actuator events.

    This may include versions from self or from other sources.
    """

    @abstractmethod
    async def on_linear_actuator(self, state: int) -> None:
        """Receive and handle a LinearActuator response."""
        pass

    @abstractmethod
    async def on_linear_actuator_position(self, position: int) -> None:
        """Receive and handle a LinearActuator/Position response."""
        pass

    @abstractmethod
    async def on_linear_actuator_position_notify(self, state: int) -> None:
        """Receive and handle a LinearActuator/Position/Notify response."""
        pass

    @abstractmethod
    async def on_linear_actuator_position_notify_interval(
        self, interval: int
    ) -> None:
        """Receive and handle a LinearActuator/Position/Notify/Interval response."""
        pass

    @abstractmethod
    async def on_linear_actuator_position_notify_change_only(
        self, state: int
    ) -> None:
        """Receive and handle a LinearActuator/Position/Notify/ChangeOnly response."""
        pass

    @abstractmethod
    async def on_linear_actuator_position_notify_number(
        self, number: int
    ) -> None:
        """Receive and handle a LinearActuator/Position/Notify/Number response."""
        pass

    @abstractmethod
    async def on_linear_actuator_smoothed_position(self, position: int) -> None:
        """Receive and handle a LinearActuator/SmoothedPosition response."""
        pass

    @abstractmethod
    async def on_linear_actuator_smoothed_position_snap_multiplier(
        self, multiplier: int
    ) -> None:
        """Receive and handle a LA/SP/SnapMultiplier response."""
        pass

    @abstractmethod
    async def on_linear_actuator_smoothed_position_range_low(
        self, position: int
    ) -> None:
        """Receive and handle a LA/SP/RangeLow response."""
        pass

    @abstractmethod
    async def on_linear_actuator_smoothed_position_range_high(
        self, position: int
    ) -> None:
        """Receive and handle a LA/SP/RangeHigh response."""
        pass

    @abstractmethod
    async def on_linear_actuator_smoothed_position_activity_threshold(
        self, position_difference: int
    ) -> None:
        """Receive and handle a LA/SP/ActivityThreshold response."""
        pass

    @abstractmethod
    async def on_linear_actuator_smoothed_position_notify(self, state: int) -> None:
        """Receive and handle a LA/SP/Notify response."""
        pass

    @abstractmethod
    async def on_linear_actuator_smoothed_position_notify_interval(
        self, interval: int
    ) -> None:
        """Receive and handle a LA/SP/Notify/Interval response."""
        pass

    @abstractmethod
    async def on_linear_actuator_smoothed_position_notify_change_only(
        self, state: int
    ) -> None:
        """Receive and handle a LA/SP/Notify/ChangeOnly response."""
        pass

    @abstractmethod
    async def on_linear_actuator_smoothed_position_notify_number(
        self, number: int
    ) -> None:
        """Receive and handle a LA/SP/Notify/Number response."""
        pass

    @abstractmethod
    async def on_linear_actuator_motor(self, duty: int) -> None:
        """Receive and handle a LinearActuator/Motor response."""
        pass

    @abstractmethod
    async def on_linear_actuator_motor_stall_protector_timeout(
        self, timeout: int
    ) -> None:
        """Receive and handle a LinearActuator/Motor/StallProtectoTimeout response."""
        pass

    @abstractmethod
    async def on_linear_actuator_motor_timer_timeout(
        self, timeout: int
    ) -> None:
        """Receive and handle a LinearActuator/Motor/TimerTimeout response."""
        pass

    @abstractmethod
    async def on_linear_actuator_motor_motor_polarity(
        self, state: int
    ) -> None:
        """Receive and handle a LinearActuator/Motor/MotorPolarity response."""
        pass

    @abstractmethod
    async def on_linear_actuator_motor_notify(self, state: int) -> None:
        """Receive and handle a LinearActuator/Motor/Notify response."""
        pass

    @abstractmethod
    async def on_linear_actuator_motor_notify_interval(self, interval: int) -> None:
        """Receive and handle a LinearActuator/Motor/Notify/Interval response."""
        pass

    @abstractmethod
    async def on_linear_actuator_motor_notify_change_only(self, state: int) -> None:
        """Receive and handle a LinearActuator/Motor/Notify/ChangeOnly response."""
        pass

    @abstractmethod
    async def on_linear_actuator_motor_notify_number(self, number: int) -> None:
        """Receive and handle a LinearActuator/Motor/Notify/Number response."""
        pass

    @abstractmethod
    async def on_linear_actuator_feedback_controller(self, state: int) -> None:
        """Receive and handle a LinearActuator/FeedbackController response."""
        pass

    @abstractmethod
    async def on_linear_actuator_feedback_controller_convergence_timeout(
        self, timeout: int
    ) -> None:
        """Receive and handle a LA/FC/ConvergenceTimeout response."""
        pass

    @abstractmethod
    async def on_linear_actuator_feedback_controller_limits_position_low(
        self, position: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Position/Low response."""
        pass

    @abstractmethod
    async def on_linear_actuator_feedback_controller_limits_position_high(
        self, position: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Position/High response."""
        pass

    @abstractmethod
    async def on_linear_actuator_feedback_controller_limits_motor_forwards_low(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Forwards/Low response."""
        pass

    @abstractmethod
    async def on_linear_actuator_feedback_controller_limits_motor_forwards_high(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Forwards/High response."""
        pass

    @abstractmethod
    async def on_linear_actuator_feedback_controller_limits_motor_backwards_low(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Backwards/Low response."""
        pass

    @abstractmethod
    async def on_linear_actuator_feedback_controller_limits_motor_backwards_high(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Backwards/High response."""
        pass

    @abstractmethod
    async def on_linear_actuator_feedback_controller_pid_kp(
        self, coefficient: int
    ) -> None:
        """Receive and handle a LA/FC/PID/Kp response."""
        pass

    @abstractmethod
    async def on_linear_actuator_feedback_controller_pid_kd(
        self, coefficient: int
    ) -> None:
        """Receive and handle a LA/FC/PID/Kd response."""
        pass

    @abstractmethod
    async def on_linear_actuator_feedback_controller_pid_ki(
        self, coefficient: int
    ) -> None:
        """Receive and handle a LA/FC/PID/Ki response."""
        pass

    @abstractmethod
    async def on_linear_actuator_feedback_controller_pid_sample_interval(
        self, interval: int
    ) -> None:
        """Receive and handle a LA/FC/PID/SampleInterval response."""
        pass


# Type-checking names
_LinearActuatorReceivers = Iterable[LinearActuatorReceiver]


# Printing

class LinearActuatorPrinter(LinearActuatorReceiver, Printer):
    """Simple class which prints received serialized messages."""

    def __init__(self, axis: str, *args, **kwargs):
        """Initialize member variables."""
        super().__init__(*args, **kwargs)
        self.axis = axis

    async def on_linear_actuator(self, state: int) -> None:
        """Receive and handle a LinearActuator response."""
        state_names = {
            1: 'Direct Motor Duty Control',
            2: 'Position Feedback Control',
            0: 'Manual Brake',
            -1: 'Stopped Stall',
            -2: 'Stopped Convergence',
            -3: 'Stopped Tiimeout'
        }
        print('{}: {}'.format(self.axis, state_names[state]))

    async def on_linear_actuator_position(self, position: int) -> None:
        """Receive and handle a LinearActuator/Position response."""
        print('{} Position: {}'.format(self.axis, position))

    async def on_linear_actuator_position_notify(self, state: int) -> None:
        """Receive and handle a LinearActuator/Position/Notify response."""
        state_names = {
            0: 'not notifying',
            1: 'notifying by iterations interval',
            2: 'notifying by time interval'
        }
        print('{} Position Notifications: {}'.format(self.axis, state_names[state]))

    async def on_linear_actuator_position_notify_interval(
        self, interval: int
    ) -> None:
        """Receive and handle a LinearActuator/Position/Notify/Interval response."""
        print('{} Position Notifications Interval: {}'.format(self.axis, interval))

    async def on_linear_actuator_position_notify_change_only(
        self, state: int
    ) -> None:
        """Receive and handle a LinearActuator/Position/Notify/ChangeOnly response."""
        print('{} Position Notifications: notify {}'.format(
            self.axis, 'only on change' if state else 'always'
        ))

    async def on_linear_actuator_position_notify_number(
        self, number: int
    ) -> None:
        """Receive and handle a LinearActuator/Position/Notify/Number response."""
        print('{} Position Notifications: notify {}'.format(
            self.axis, '{} times' if number >= 0 else 'forever'
        ))

    async def on_linear_actuator_smoothed_position(self, position: int) -> None:
        """Receive and handle a LinearActuator/SmoothedPosition response."""
        print('{} Smoothed Position: {}'.format(self.axis, position))

    async def on_linear_actuator_smoothed_position_snap_multiplier(
        self, multiplier: int
    ) -> None:
        """Receive and handle a LA/SP/SnapMultiplier response."""
        print('{} Smoothed Position Snap Multiplier: {}'.format(
            self.axis, multiplier
        ))

    async def on_linear_actuator_smoothed_position_range_low(
        self, position: int
    ) -> None:
        """Receive and handle a LA/SP/RangeLow response."""
        print('{} Smoothed Position Range: >= {}'.format(
            self.axis, position
        ))

    async def on_linear_actuator_smoothed_position_range_high(
        self, position: int
    ) -> None:
        """Receive and handle a LA/SP/RangeHigh response."""
        print('{} Smoothed Position Range: <= {}'.format(
            self.axis, position
        ))

    async def on_linear_actuator_smoothed_position_activity_threshold(
        self, position_difference: int
    ) -> None:
        """Receive and handle a LA/SP/ActivityThreshold response."""
        print('{} Smoothed Position Sleeping: wake above {}'.format(
            self.axis, position_difference
        ))

    async def on_linear_actuator_smoothed_position_notify(self, state: int) -> None:
        """Receive and handle a LA/SP/Notify response."""
        state_names = {
            0: 'not notifying',
            1: 'notifying by iterations interval',
            2: 'notifying by time interval'
        }
        print('{} Smoothed Position Notifications: {}'.format(self.axis, state_names[state]))

    async def on_linear_actuator_smoothed_position_notify_interval(
        self, interval: int
    ) -> None:
        """Receive and handle a LA/SP/Notify/Interval response."""
        print('{} Smoothed Position Notifications Interval: {}'.format(self.axis, interval))

    async def on_linear_actuator_smoothed_position_notify_change_only(
        self, state: int
    ) -> None:
        """Receive and handle a LA/SP/Notify/ChangeOnly response."""
        print('{} Smoothed Position Notifications: notify {}'.format(
            self.axis, 'only on change' if state else 'always'
        ))

    async def on_linear_actuator_smoothed_position_notify_number(
        self, number: int
    ) -> None:
        """Receive and handle a LA/SP/Notify/Number response."""
        """Receive and handle a LinearActuator/Position/Notify/Number response."""
        print('{} Smoothed Position Notifications: notify {}'.format(
            self.axis, '{} times' if number >= 0 else 'forever'
        ))

    async def on_linear_actuator_motor(self, duty: int) -> None:
        """Receive and handle a LinearActuator/Motor response."""
        print('{} Motor: {}'.format(
            self.axis, 'braking' if duty == 0 else 'running at {}'.format(duty)
        ))

    async def on_linear_actuator_motor_stall_protector_timeout(
        self, timeout: int
    ) -> None:
        """Receive and handle a LinearActuator/Motor/StallProtectorTimeout response."""
        print('{} Motor Stall Protector: {}'.format(
            self.axis, 'disabled' if timeout == 0 else 'timeout {}'.format(timeout)
        ))

    async def on_linear_actuator_motor_timer_timeout(
        self, timeout: int
    ) -> None:
        """Receive and handle a LinearActuator/Motor/TimerTimeout response."""
        print('{} Motor Timer: {}'.format(
            self.axis, 'disabled' if timeout == 0 else 'timeout {}'.format(timeout)
        ))

    async def on_linear_actuator_motor_motor_polarity(
        self, state: int
    ) -> None:
        """Receive and handle a LinearActuator/Motor/MotorPolarity response."""
        print('{} Motor: polarity{}'.format(
            self.axis, 'flipped' if state == -1 else 'normal'
        ))

    async def on_linear_actuator_motor_notify(self, state: int) -> None:
        """Receive and handle a LinearActuator/Motor/Notify response."""
        state_names = {
            0: 'not notifying',
            1: 'notifying by iterations interval',
            2: 'notifying by time interval'
        }
        print('{} Motor Duty Notifications: {}'.format(self.axis, state_names[state]))

    async def on_linear_actuator_motor_notify_interval(self, interval: int) -> None:
        """Receive and handle a LinearActuator/Motor/Notify/Interval response."""
        print('{} Motor Duty Notifications Interval: {}'.format(self.axis, interval))

    async def on_linear_actuator_motor_notify_change_only(self, state: int) -> None:
        """Receive and handle a LinearActuator/Motor/Notify/ChangeOnly response."""
        print('{} Motor Duty Notifications: notify {}'.format(
            self.axis, 'only on change' if state else 'always'
        ))

    async def on_linear_actuator_motor_notify_number(self, number: int) -> None:
        """Receive and handle a LinearActuator/Motor/Notify/Number response."""
        print('{} Motor Duty Notifications: notify {}'.format(
            self.axis, '{} times' if number >= 0 else 'forever'
        ))

    async def on_linear_actuator_feedback_controller(self, position: int) -> None:
        """Receive and handle a LinearActuator/FeedbackController response."""
        print('{} Feedback Controller Target: {}'.format(self.axis, position))

    async def on_linear_actuator_feedback_controller_convergence_timeout(
        self, timeout: int
    ) -> None:
        """Receive and handle a LA/FC/ConvergenceTimeout response."""
        print('{} Feedback Controller Convergence Timer: {}'.format(
            self.axis, 'disabled' if timeout == 0 else 'timeout {}'.format(timeout)
        ))

    async def on_linear_actuator_feedback_controller_limits_position_low(
        self, position: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Position/Low response."""
        print('{} Feedback Controller Position Range: >= {}'.format(
            self.axis, position
        ))

    async def on_linear_actuator_feedback_controller_limits_position_high(
        self, position: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Position/High response."""
        print('{} Feedback Controller Position Range: <= {}'.format(
            self.axis, position
        ))

    async def on_linear_actuator_feedback_controller_limits_motor_forwards_low(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Forwards/Low response."""
        print('{} Feedback Controller Motor Duty Forwards Range: >= {}'.format(
            self.axis, duty
        ))

    async def on_linear_actuator_feedback_controller_limits_motor_forwards_high(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Forwards/High response."""
        print('{} Feedback Controller Motor Duty Forwards Range: <= {}'.format(
            self.axis, duty
        ))

    async def on_linear_actuator_feedback_controller_limits_motor_backwards_low(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Backwards/Low response."""
        print('{} Feedback Controller Motor Duty Backwards Range: >= {}'.format(
            self.axis, duty
        ))

    async def on_linear_actuator_feedback_controller_limits_motor_backwards_high(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Backwards/High response."""
        print('{} Feedback Controller Motor Duty Backwards Range: <= {}'.format(
            self.axis, duty
        ))

    async def on_linear_actuator_feedback_controller_pid_kp(
        self, coefficient: int
    ) -> None:
        """Receive and handle a LA/FC/PID/Kp response."""
        print('{} Feedback Controller PID Kp: {}'.format(self.axis, coefficient))

    async def on_linear_actuator_feedback_controller_pid_kd(
        self, coefficient: int
    ) -> None:
        """Receive and handle a LA/FC/PID/Kd response."""
        print('{} Feedback Controller PID Kd: {}'.format(self.axis, coefficient))

    async def on_linear_actuator_feedback_controller_pid_ki(
        self, coefficient: int
    ) -> None:
        """Receive and handle a LA/FC/PID/Ki response."""
        print('{} Feedback Controller PID Ki: {}'.format(self.axis, coefficient))

    async def on_linear_actuator_feedback_controller_pid_sample_interval(
        self, interval: int
    ) -> None:
        """Receive and handle a LA/FC/PID/SampleInterval response."""
        print('{} Feedback Controller PID Sample Interval: {}'.format(
            self.axis, interval
        ))


class LinearActuatorNotifyProtocol(ChannelHandlerTreeChildNode, CommandIssuer):
    """Notifies on the parent's value."""

    def __init__(self, parent, **kwargs):
        """Initialize member variables."""
        super().__init__(parent, 'Notify', 'n', **kwargs)
        self.command_receivers = self.parent.command_receivers
        self.linear_actuator_receivers = self.parent.linear_actuator_receivers

    async def notify_linear_actuator_receivers(self, state: int) -> None:
        """Notify all receivers of received LA/_/Notify response."""
        for receiver in self.linear_actuator_receivers:
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

    async def notify_linear_actuator_receivers_interval(self, interval: int) -> None:
        """Notify all receivers of received LA/_/Notify/Interval response."""
        for receiver in self.linear_actuator_receivers:
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

    async def notify_linear_actuator_receivers_change_only(self, state: int) -> None:
        """Notify all receivers of received LA/_/Notify/ChangeOnly response."""
        for receiver in self.linear_actuator_receivers:
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

    async def notify_linear_actuator_receivers_number(self, number: int) -> None:
        """Notify all receivers of received LA/_/Notify/number response."""
        for receiver in self.linear_actuator_receivers:
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
        await self.notify_linear_actuator_receivers_interval(message.payload)

    async def on_received_message_change_only(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_linear_actuator_receivers_change_only(message.payload)

    async def on_received_message_number(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_linear_actuator_receivers_number(message.payload)

    async def on_any_message(self, message):
        """Handle any message whether or not it is recognized as by the node."""
        if message.payload is None:
            return
        self.on_response(message.channel)

    async def on_received_message(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the node."""
        if message.payload is None:
            return
        if message.channel == self.name_path:
            await self.notify_linear_actuator_receivers(message.payload)


class LinearActuatorPositionProtocol(ChannelHandlerTreeChildNode, CommandIssuer):
    """Notifies on the linear actuator's position."""

    def __init__(self, parent, **kwargs):
        """Initialize member variables."""
        super().__init__(parent, 'Position', 'p', **kwargs)
        self.command_receivers = self.parent.command_receivers
        self.linear_actuator_receivers = self.parent.linear_actuator_receivers

        self.notify = LinearActuatorNotifyProtocol(self)

    async def notify_linear_actuator_receivers(self, position: int) -> None:
        """Notify all receivers of received LA/Position response."""
        for receiver in self.linear_actuator_receivers:
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

    async def on_any_message(self, message):
        """Handle any message whether or not it is recognized as by the node."""
        if message.payload is None:
            return
        self.on_response(message.channel)

    async def on_received_message(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the node."""
        if message.payload is None:
            return
        if message.channel == self.name_path:
            await self.notify_linear_actuator_receivers(message.payload)


class LinearActuatorSmoothedPositionProtocol(ChannelHandlerTreeChildNode, CommandIssuer):
    """Notifies on the linear actuator's position."""

    def __init__(self, parent, **kwargs):
        """Initialize member variables."""
        super().__init__(parent, 'SmoothedPosition', 's', **kwargs)
        self.command_receivers = self.parent.command_receivers
        self.linear_actuator_receivers = self.parent.linear_actuator_receivers

        self.notify = LinearActuatorNotifyProtocol(self)

    async def notify_linear_actuator_receivers(self, position: int) -> None:
        """Notify all receivers of received LA/SmoothedPosition response."""
        for receiver in self.linear_actuator_receivers:
            await receiver.on_linear_actuator_smoothed_position(position)

    async def notify_linear_actuator_receivers_snap_multiplier(
        self, multiplier: int
    ) -> None:
        """Notify all receivers of received LA/SP/SnapMultiplier response."""
        for receiver in self.linear_actuator_receivers:
            await receiver.on_linear_actuator_smoothed_position_snap_multiplier(
                multiplier
            )

    async def notify_linear_actuator_receivers_range_low(
        self, position: int
    ) -> None:
        """Notify all receivers of received LA/SP/RangeLow response."""
        for receiver in self.linear_actuator_receivers:
            await receiver.on_linear_actuator_smoothed_position_range_low(
                position
            )

    async def notify_linear_actuator_receivers_range_high(
        self, position: int
    ) -> None:
        """Notify all receivers of received LA/SP/RangeHigh response."""
        for receiver in self.linear_actuator_receivers:
            await receiver.on_linear_actuator_smoothed_position_range_high(
                position
            )

    async def notify_linear_actuator_receivers_activity_threshold(
        self, position_difference: int
    ) -> None:
        """Notify all receivers of received LA/SP/ActivityThreshold response."""
        for receiver in self.linear_actuator_receivers:
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
        await self.notify_linear_actuator_receivers_snap_multiplier(message.payload)

    async def on_received_message_range_low(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_linear_actuator_receivers_range_low(message.payload)

    async def on_received_message_range_high(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_linear_actuator_receivers_range_high(message.payload)

    async def on_received_message_activity_threshold(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_linear_actuator_receivers_activity_threshold(message.payload)

    async def on_any_message(self, message):
        """Handle any message whether or not it is recognized as by the node."""
        if message.payload is None:
            return
        self.on_response(message.channel)

    async def on_received_message(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the node."""
        if message.payload is None:
            return
        if message.channel == self.name_path:
            await self.notify_linear_actuator_receivers(message.payload)


class LinearActuatorMotorProtocol(ChannelHandlerTreeChildNode, CommandIssuer):
    """Notifies on the linear actuator's motor duty."""

    def __init__(self, parent, **kwargs):
        """Initialize member variables."""
        super().__init__(parent, 'Motor', 'm', **kwargs)
        self.command_receivers = self.parent.command_receivers
        self.linear_actuator_receivers = self.parent.linear_actuator_receivers

        self.notify = LinearActuatorNotifyProtocol(self)

    async def notify_linear_actuator_receivers(self, position: int) -> None:
        """Notify all receivers of received LA/Motor response."""
        for receiver in self.linear_actuator_receivers:
            await receiver.on_linear_actuator_position(position)

    async def notify_linear_actuator_receivers_stall_protector_timeout(
        self, timeout: int
    ) -> None:
        """Notify all receivers of received LA/Motor/StallProtectorTimeout response."""
        for receiver in self.linear_actuator_receivers:
            await receiver.on_linear_actuator_motor_stall_protector(timeout)

    async def notify_linear_actuator_receivers_timer_timeout(
        self, timeout: int
    ) -> None:
        """Notify all receivers of received LA/Motor/TimerTimeout response."""
        for receiver in self.linear_actuator_receivers:
            await receiver.on_linear_actuator_motor_timer_timeout(timeout)

    async def notify_linear_actuator_receivers_motor_polarity(
        self, state: int
    ) -> None:
        """Notify all receivers of received LA/Motor/MotorPolarity response."""
        for receiver in self.linear_actuator_receivers:
            await receiver.on_linear_actuator_motor_motor_polarity(state)

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
            self.name_path,
            self.parent.position.name_path,
            self.name_path,
            self.parent.name_path
        ]
        logger.debug('Starting motor direct duty control...')
        await self.issue_command(Command(message, wait_channels))
        logger.debug('Finished motor direct duty control!')

    async def request_stall_protector_timeout(self, timeout: Optional[int]=None):
        """Send a LA/Motor/StallProtectorTimeout request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path + 's', timeout)
        await self.issue_command(Command(message))

    async def request_timer_timeout(self, timeout: Optional[int]=None):
        """Send a LA/Motor/TimerTimeout request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path + 't', timeout)
        await self.issue_command(Command(message))

    async def request_motor_polarity(self, state: Optional[int]=None):
        """Send a LA/Motor/MotorPolarity request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path + 'p', state)
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
            't': self.on_received_message_timer_timeout,
            'p': self.on_received_message_motor_polarity
        }

    async def on_received_message_snap_multiplier(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_linear_actuator_receivers_snap_multiplier(message.payload)

    async def on_received_message_timer_timeout(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_linear_actuator_receivers_timer_timeout(message.payload)

    async def on_received_message_motor_polarity(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_linear_actuator_receivers_motor_polarity(message.payload)

    async def on_any_message(self, message):
        """Handle any message whether or not it is recognized as by the node."""
        if message.payload is None:
            return
        self.on_response(message.channel)

    async def on_received_message(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the node."""
        if message.payload is None:
            return
        if message.channel == self.name_path:
            await self.notify_linear_actuator_receivers(message.payload)


class LinearActuatorProtocol(ChannelHandlerTreeChildNode, CommandIssuer):
    """Sets the built-in LED."""

    def __init__(
        self, node_channel, node_name,
        linear_actuator_receivers: Optional[_LinearActuatorReceivers]=None, **kwargs
    ):
        """Initialize member variables."""
        super().__init__(None, node_channel, node_name, **kwargs)
        self.linear_actuator_receivers: List[LinearActuatorReceiver] = []
        if linear_actuator_receivers:
            self.linear_actuator_receivers = [
                receiver for receiver in linear_actuator_receivers
            ]

        self.position = LinearActuatorPositionProtocol(self, **kwargs)
        self.smoothed_position = LinearActuatorSmoothedPositionProtocol(self, **kwargs)
        self.motor = LinearActuatorMotorProtocol(self, **kwargs)
        # self.feedback_controller = LinearActuatorFeedbackControllerProtocol(self, **kwargs)

    async def notify_linear_actuator_receivers(self, state: int) -> None:
        """Notify all receivers of received LinearActuator response."""
        for receiver in self.linear_actuator_receivers:
            await receiver.on_linear_actuator(state)

    # Commands

    async def request(self, state: Optional[int]=None):
        """Send a LinearActuator request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path, state)
        await self.issue_command(Command(message))

    # Implement ChannelTreeNode

    @property
    def node_channel(self) -> str:
        """Return the channel of the node as a string."""
        return 'LinearActuator'

    @property
    def node_name(self) -> str:
        """Return the channel name of the node as a string."""
        return 'p'

    @property
    def children(self):
        """Return a dict of the child ChannelTreeNodes keyed by prefixes."""
        return {
            self.position.node_name: self.position,
            self.smoothed_position.node_name: self.smoothed_position,
            self.motor.node_name: self.motor,
            # self.feedback_controller.node_name: self.feedback_controller
        }

    # Implement MessageReceiver

    async def on_any_message(self, message):
        """Handle any message whether or not it is recognized as by the node."""
        if message.payload is None:
            return
        self.on_response(message.channel)

    async def on_received_message(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the node."""
        if message.payload is None:
            return
        # TODO: validate the channel name
        if message.channel == self.name_path:
            await self.notify_linear_actuator_receivers(message.payload)
