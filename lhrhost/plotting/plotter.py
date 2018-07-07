"""Support for real-time plotting of LinearActuator state."""
# Standard imports
import datetime

# External imports
from bokeh.client import push_session
from bokeh.models import ColumnDataSource, DatetimeTickFormatter
from bokeh.plotting import curdoc, figure

# Local package imports
from lhrhost.protocol.linear_actuator.linear_actuator import Receiver as LinearActuatorReceiver


class Plotter():
    """Plots received data."""

    def __init__(self, title, plot_width=800, plot_height=400):
        """Initialize membeer variables."""
        self.plot_source = ColumnDataSource(data={
            'time': [],
            'position': [],
            'duty': []
        })
        self.fig = figure(
            plot_width=plot_width, plot_height=plot_height,
            title=title
        )
        self.fig.xaxis.formatter = DatetimeTickFormatter()
        self.position_line = self.fig.line(x='time', y='position', source=self.plot_source)
        self.duty_line = self.fig.line(x='time', y='duty', source=self.plot_source)
        self.session = None

    def show(self):
        """Create the plot figure."""
        self.session = push_session(curdoc(), session_id='main')
        self.session.show(self.fig)

    def add_point(self, position, duty):
        """Add a point to the plot."""
        self.plot_source.stream({
            'time': [datetime.datetime.now()],
            'position': [position],
            'duty': [duty]
        })


class LinearActuatorPlotter(LinearActuatorReceiver):
    """Simple class which prints received serialized messages."""

    def __init__(self, *args, **kwargs):
        """Initialize member variables."""
        super().__init__(*args, **kwargs)
        self.plotter = Plotter()
        self.position = None
        self.duty = None

    async def on_linear_actuator(self, state: int) -> None:
        """Receive and handle a LinearActuator response."""
        pass

    async def on_linear_actuator_position(self, position: int) -> None:
        """Receive and handle a LinearActuator/Position response."""
        self.position = position
        self.plotter.add_point(self.position, self.duty)

    async def on_linear_actuator_position_notify(self, state: int) -> None:
        """Receive and handle a LinearActuator/Position/Notify response."""
        pass

    async def on_linear_actuator_position_notify_interval(
        self, interval: int
    ) -> None:
        """Receive and handle a LinearActuator/Position/Notify/Interval response."""
        pass

    async def on_linear_actuator_position_notify_change_only(
        self, state: int
    ) -> None:
        """Receive and handle a LinearActuator/Position/Notify/ChangeOnly response."""
        pass

    async def on_linear_actuator_position_notify_number(
        self, number: int
    ) -> None:
        """Receive and handle a LinearActuator/Position/Notify/Number response."""
        pass

    async def on_linear_actuator_smoothed_position(self, position: int) -> None:
        """Receive and handle a LinearActuator/SmoothedPosition response."""
        pass

    async def on_linear_actuator_smoothed_position_snap_multiplier(
        self, multiplier: int
    ) -> None:
        """Receive and handle a LA/SP/SnapMultiplier response."""
        pass

    async def on_linear_actuator_smoothed_position_range_low(
        self, position: int
    ) -> None:
        """Receive and handle a LA/SP/RangeLow response."""
        pass

    async def on_linear_actuator_smoothed_position_range_high(
        self, position: int
    ) -> None:
        """Receive and handle a LA/SP/RangeHigh response."""
        pass

    async def on_linear_actuator_smoothed_position_activity_threshold(
        self, position_difference: int
    ) -> None:
        """Receive and handle a LA/SP/ActivityThreshold response."""
        pass

    async def on_linear_actuator_smoothed_position_notify(self, state: int) -> None:
        """Receive and handle a LA/SP/Notify response."""
        pass

    async def on_linear_actuator_smoothed_position_notify_interval(
        self, interval: int
    ) -> None:
        """Receive and handle a LA/SP/Notify/Interval response."""
        pass

    async def on_linear_actuator_smoothed_position_notify_change_only(
        self, state: int
    ) -> None:
        """Receive and handle a LA/SP/Notify/ChangeOnly response."""
        pass

    async def on_linear_actuator_smoothed_position_notify_number(
        self, number: int
    ) -> None:
        """Receive and handle a LA/SP/Notify/Number response."""
        """Receive and handle a LinearActuator/Position/Notify/Number response."""
        pass

    async def on_linear_actuator_motor(self, duty: int) -> None:
        """Receive and handle a LinearActuator/Motor response."""
        self.duty = duty
        self.plotter.add_point(self.position, self.duty)

    async def on_linear_actuator_motor_stall_protector_timeout(
        self, timeout: int
    ) -> None:
        """Receive and handle a LinearActuator/Motor/StallProtectorTimeout response."""
        pass

    async def on_linear_actuator_motor_timer_timeout(
        self, timeout: int
    ) -> None:
        """Receive and handle a LinearActuator/Motor/TimerTimeout response."""
        pass

    async def on_linear_actuator_motor_motor_polarity(
        self, state: int
    ) -> None:
        """Receive and handle a LinearActuator/Motor/MotorPolarity response."""
        pass

    async def on_linear_actuator_motor_notify(self, state: int) -> None:
        """Receive and handle a LinearActuator/Motor/Notify response."""
        pass

    async def on_linear_actuator_motor_notify_interval(self, interval: int) -> None:
        """Receive and handle a LinearActuator/Motor/Notify/Interval response."""
        pass

    async def on_linear_actuator_motor_notify_change_only(self, state: int) -> None:
        """Receive and handle a LinearActuator/Motor/Notify/ChangeOnly response."""
        pass

    async def on_linear_actuator_motor_notify_number(self, number: int) -> None:
        """Receive and handle a LinearActuator/Motor/Notify/Number response."""
        pass

    async def on_linear_actuator_feedback_controller(self, position: int) -> None:
        """Receive and handle a LinearActuator/FeedbackController response."""
        pass

    async def on_linear_actuator_feedback_controller_convergence_timeout(
        self, timeout: int
    ) -> None:
        """Receive and handle a LA/FC/ConvergenceTimeout response."""
        pass

    async def on_linear_actuator_feedback_controller_limits_position_low(
        self, position: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Position/Low response."""
        pass

    async def on_linear_actuator_feedback_controller_limits_position_high(
        self, position: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Position/High response."""
        pass

    async def on_linear_actuator_feedback_controller_limits_motor_forwards_low(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Forwards/Low response."""
        pass

    async def on_linear_actuator_feedback_controller_limits_motor_forwards_high(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Forwards/High response."""
        pass

    async def on_linear_actuator_feedback_controller_limits_motor_backwards_low(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Backwards/Low response."""
        pass

    async def on_linear_actuator_feedback_controller_limits_motor_backwards_high(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Backwards/High response."""
        pass

    async def on_linear_actuator_feedback_controller_pid_kp(
        self, coefficient: int
    ) -> None:
        """Receive and handle a LA/FC/PID/Kp response."""
        pass

    async def on_linear_actuator_feedback_controller_pid_kd(
        self, coefficient: int
    ) -> None:
        """Receive and handle a LA/FC/PID/Kd response."""
        pass

    async def on_linear_actuator_feedback_controller_pid_ki(
        self, coefficient: int
    ) -> None:
        """Receive and handle a LA/FC/PID/Ki response."""
        pass

    async def on_linear_actuator_feedback_controller_pid_sample_interval(
        self, interval: int
    ) -> None:
        """Receive and handle a LA/FC/PID/SampleInterval response."""
        pass
