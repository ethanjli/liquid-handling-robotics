"""LinearActuator channels of linear actuator protocol."""

# Standard imports
import asyncio
import logging
from abc import abstractmethod
from typing import Iterable, List, Optional

# Local package imports
from lhrhost.messaging.presentation import Message
from lhrhost.protocol import Command, ProtocolHandlerNode
from lhrhost.protocol.linear_actuator.motor import Protocol as MotorProtocol
from lhrhost.protocol.linear_actuator.position import Protocol as PositionProtocol
from lhrhost.protocol.linear_actuator.smoothed_position import Protocol as \
    SmoothedPositionProtocol
from lhrhost.protocol.linear_actuator.feedback_controller import Protocol as \
    FeedbackControllerProtocol
from lhrhost.util.interfaces import InterfaceClass
from lhrhost.util.printing import Printer

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# Receipt of LinearActuator

class Receiver(object, metaclass=InterfaceClass):
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
_Receivers = Iterable[Receiver]


# Printing

class Printer(Receiver, Printer):
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
            -3: 'Stopped Timeout'
        }
        self.print('{}: {}'.format(self.axis, state_names[state]))

    async def on_linear_actuator_position(self, position: int) -> None:
        """Receive and handle a LinearActuator/Position response."""
        self.print('{} Position: {}'.format(self.axis, position))

    async def on_linear_actuator_position_notify(self, state: int) -> None:
        """Receive and handle a LinearActuator/Position/Notify response."""
        state_names = {
            0: 'not notifying',
            1: 'notifying by iterations interval',
            2: 'notifying by time interval'
        }
        self.print('{} Position Notifications: {}'.format(self.axis, state_names[state]))

    async def on_linear_actuator_position_notify_interval(
        self, interval: int
    ) -> None:
        """Receive and handle a LinearActuator/Position/Notify/Interval response."""
        self.print('{} Position Notifications Interval: {}'.format(self.axis, interval))

    async def on_linear_actuator_position_notify_change_only(
        self, state: int
    ) -> None:
        """Receive and handle a LinearActuator/Position/Notify/ChangeOnly response."""
        self.print('{} Position Notifications: notify {}'.format(
            self.axis, 'only on change' if state else 'always'
        ))

    async def on_linear_actuator_position_notify_number(
        self, number: int
    ) -> None:
        """Receive and handle a LinearActuator/Position/Notify/Number response."""
        self.print('{} Position Notifications: notify {}'.format(
            self.axis, '{} times'.format(number) if number >= 0 else 'forever'
        ))

    async def on_linear_actuator_smoothed_position(self, position: int) -> None:
        """Receive and handle a LinearActuator/SmoothedPosition response."""
        self.print('{} Smoothed Position: {}'.format(self.axis, position))

    async def on_linear_actuator_smoothed_position_snap_multiplier(
        self, multiplier: int
    ) -> None:
        """Receive and handle a LA/SP/SnapMultiplier response."""
        self.print('{} Smoothed Position Snap Multiplier: {}'.format(
            self.axis, multiplier
        ))

    async def on_linear_actuator_smoothed_position_range_low(
        self, position: int
    ) -> None:
        """Receive and handle a LA/SP/RangeLow response."""
        self.print('{} Smoothed Position: >= {}'.format(
            self.axis, position
        ))

    async def on_linear_actuator_smoothed_position_range_high(
        self, position: int
    ) -> None:
        """Receive and handle a LA/SP/RangeHigh response."""
        self.print('{} Smoothed Position: <= {}'.format(
            self.axis, position
        ))

    async def on_linear_actuator_smoothed_position_activity_threshold(
        self, position_difference: int
    ) -> None:
        """Receive and handle a LA/SP/ActivityThreshold response."""
        self.print('{} Smoothed Position Sleeping: wake above {}'.format(
            self.axis, position_difference
        ))

    async def on_linear_actuator_smoothed_position_notify(self, state: int) -> None:
        """Receive and handle a LA/SP/Notify response."""
        state_names = {
            0: 'not notifying',
            1: 'notifying by iterations interval',
            2: 'notifying by time interval'
        }
        self.print('{} Smoothed Position Notifications: {}'.format(self.axis, state_names[state]))

    async def on_linear_actuator_smoothed_position_notify_interval(
        self, interval: int
    ) -> None:
        """Receive and handle a LA/SP/Notify/Interval response."""
        self.print('{} Smoothed Position Notifications Interval: {}'.format(self.axis, interval))

    async def on_linear_actuator_smoothed_position_notify_change_only(
        self, state: int
    ) -> None:
        """Receive and handle a LA/SP/Notify/ChangeOnly response."""
        self.print('{} Smoothed Position Notifications: notify {}'.format(
            self.axis, 'only on change' if state else 'always'
        ))

    async def on_linear_actuator_smoothed_position_notify_number(
        self, number: int
    ) -> None:
        """Receive and handle a LA/SP/Notify/Number response."""
        """Receive and handle a LinearActuator/Position/Notify/Number response."""
        self.print('{} Smoothed Position Notifications: notify {}'.format(
            self.axis, '{} times' if number >= 0 else 'forever'
        ))

    async def on_linear_actuator_motor(self, duty: int) -> None:
        """Receive and handle a LinearActuator/Motor response."""
        self.print('{} Motor: {}'.format(
            self.axis, 'braking' if duty == 0 else 'running at {}'.format(duty)
        ))

    async def on_linear_actuator_motor_stall_protector_timeout(
        self, timeout: int
    ) -> None:
        """Receive and handle a LinearActuator/Motor/StallProtectorTimeout response."""
        self.print('{} Motor Stall Protector: {}'.format(
            self.axis, 'disabled' if timeout == 0 else 'timeout {}'.format(timeout)
        ))

    async def on_linear_actuator_motor_timer_timeout(
        self, timeout: int
    ) -> None:
        """Receive and handle a LinearActuator/Motor/TimerTimeout response."""
        self.print('{} Motor Timer: {}'.format(
            self.axis, 'disabled' if timeout == 0 else 'timeout {}'.format(timeout)
        ))

    async def on_linear_actuator_motor_motor_polarity(
        self, state: int
    ) -> None:
        """Receive and handle a LinearActuator/Motor/MotorPolarity response."""
        self.print('{} Motor: polarity {}'.format(
            self.axis, 'flipped' if state == -1 else 'normal'
        ))

    async def on_linear_actuator_motor_notify(self, state: int) -> None:
        """Receive and handle a LinearActuator/Motor/Notify response."""
        state_names = {
            0: 'not notifying',
            1: 'notifying by iterations interval',
            2: 'notifying by time interval'
        }
        self.print('{} Motor Duty Notifications: {}'.format(self.axis, state_names[state]))

    async def on_linear_actuator_motor_notify_interval(self, interval: int) -> None:
        """Receive and handle a LinearActuator/Motor/Notify/Interval response."""
        self.print('{} Motor Duty Notifications Interval: {}'.format(self.axis, interval))

    async def on_linear_actuator_motor_notify_change_only(self, state: int) -> None:
        """Receive and handle a LinearActuator/Motor/Notify/ChangeOnly response."""
        self.print('{} Motor Duty Notifications: notify {}'.format(
            self.axis, 'only on change' if state else 'always'
        ))

    async def on_linear_actuator_motor_notify_number(self, number: int) -> None:
        """Receive and handle a LinearActuator/Motor/Notify/Number response."""
        self.print('{} Motor Duty Notifications: notify {}'.format(
            self.axis, '{} times' if number >= 0 else 'forever'
        ))

    async def on_linear_actuator_feedback_controller(self, position: int) -> None:
        """Receive and handle a LinearActuator/FeedbackController response."""
        self.print('{} Feedback Controller Target: {}'.format(self.axis, position))

    async def on_linear_actuator_feedback_controller_convergence_timeout(
        self, timeout: int
    ) -> None:
        """Receive and handle a LA/FC/ConvergenceTimeout response."""
        self.print('{} Feedback Controller Convergence Timer: {}'.format(
            self.axis, 'disabled' if timeout == 0 else 'timeout {}'.format(timeout)
        ))

    async def on_linear_actuator_feedback_controller_limits_position_low(
        self, position: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Position/Low response."""
        self.print('{} Feedback Controller Position: >= {}'.format(
            self.axis, position
        ))

    async def on_linear_actuator_feedback_controller_limits_position_high(
        self, position: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Position/High response."""
        self.print('{} Feedback Controller Position: <= {}'.format(
            self.axis, position
        ))

    async def on_linear_actuator_feedback_controller_limits_motor_forwards_low(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Forwards/Low response."""
        self.print('{} Feedback Controller Motor Duty Forwards: brake below {}'.format(
            self.axis, duty
        ))

    async def on_linear_actuator_feedback_controller_limits_motor_forwards_high(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Forwards/High response."""
        self.print('{} Feedback Controller Motor Duty Forwards: saturate above {}'.format(
            self.axis, duty
        ))

    async def on_linear_actuator_feedback_controller_limits_motor_backwards_low(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Backwards/Low response."""
        self.print('{} Feedback Controller Motor Duty Backwards: brake above {}'.format(
            self.axis, duty
        ))

    async def on_linear_actuator_feedback_controller_limits_motor_backwards_high(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Backwards/High response."""
        self.print('{} Feedback Controller Motor Duty Backwards: saturate below {}'.format(
            self.axis, duty
        ))

    async def on_linear_actuator_feedback_controller_pid_kp(
        self, coefficient: int
    ) -> None:
        """Receive and handle a LA/FC/PID/Kp response."""
        self.print('{} Feedback Controller PID Kp: {}'.format(self.axis, coefficient))

    async def on_linear_actuator_feedback_controller_pid_kd(
        self, coefficient: int
    ) -> None:
        """Receive and handle a LA/FC/PID/Kd response."""
        self.print('{} Feedback Controller PID Kd: {}'.format(self.axis, coefficient))

    async def on_linear_actuator_feedback_controller_pid_ki(
        self, coefficient: int
    ) -> None:
        """Receive and handle a LA/FC/PID/Ki response."""
        self.print('{} Feedback Controller PID Ki: {}'.format(self.axis, coefficient))

    async def on_linear_actuator_feedback_controller_pid_sample_interval(
        self, interval: int
    ) -> None:
        """Receive and handle a LA/FC/PID/SampleInterval response."""
        self.print('{} Feedback Controller PID Sample Interval: {}'.format(
            self.axis, interval
        ))


class Protocol(ProtocolHandlerNode):
    """Notifies on the linear actuator's state."""

    def __init__(
        self, node_channel, node_name,
        response_receivers: Optional[_Receivers]=None, **kwargs
    ):
        """Initialize member variables."""
        super().__init__(node_channel, node_name, **kwargs)
        self.response_receivers: List[Receiver] = []
        if response_receivers:
            self.response_receivers = [
                receiver for receiver in response_receivers
            ]

        self.position = PositionProtocol(parent=self, **kwargs)
        self.smoothed_position = SmoothedPositionProtocol(parent=self, **kwargs)
        self.motor = MotorProtocol(parent=self, **kwargs)
        self.feedback_controller = FeedbackControllerProtocol(parent=self, **kwargs)

        self.initialized = asyncio.Event()

    # Commands

    async def request(self, state: Optional[int]=None):
        """Send a LinearActuator request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path, state)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    @property
    def children_list(self):
        """Return a list of child nodes."""
        return [
            self.position, self.smoothed_position,
            self.motor, self.feedback_controller
        ]

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_linear_actuator

    async def on_received_message(self, channel_name_remainder, message) -> None:
        """Handle received message."""
        await super().on_received_message(channel_name_remainder, message)
        self.initialized.set()
