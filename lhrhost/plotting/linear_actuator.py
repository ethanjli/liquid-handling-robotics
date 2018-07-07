"""Support for real-time plotting of LinearActuator state."""
# Standard imports
import datetime

# External imports
from bokeh import layouts
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, annotations, arrow_heads
from bokeh.plotting import figure

# Local package imports
from lhrhost.plotting import DocumentLayout
from lhrhost.protocol.linear_actuator.linear_actuator \
    import Receiver as LinearActuatorReceiver


class Plotter(DocumentLayout):
    """Plots received data."""

    def __init__(
        self, title, rollover=500,
        plot_width=800, plot_height=400, line_width=2
    ):
        """Initialize member variables."""
        self.rollover = rollover
        self.init_position_plot(title, plot_width, plot_height, line_width)
        self.init_duty_plot(title, plot_width, plot_height, line_width)
        self.last_position_time = None
        self.last_position = None
        self.last_duty_time = None
        self.last_duty = None

        self.column_layout = layouts.column(self.position_fig, self.duty_fig)

        self.session = None

    def init_position_plot(self, title, plot_width, plot_height, line_width):
        """Initialize member variables for position plotting."""
        self.position_source = ColumnDataSource({
            'time': [],
            'position': []
        })
        self.position_fig = figure(
            title='{}: {}'.format(title, 'Actuator Position'),
            plot_width=plot_width, plot_height=plot_height
        )
        self.position_fig.xaxis.axis_label = 'Time from Start (s)'
        self.position_fig.xaxis.formatter = DatetimeTickFormatter()
        self.position_fig.yaxis.axis_label = 'Position'
        self.position_line = self.position_fig.line(
            x='time', y='position', source=self.position_source, line_width=line_width
        )

    def init_duty_plot(self, title, plot_width, plot_height, line_width):
        """Initialize member variables for motor duty cycle plotting."""
        self.duty_source = ColumnDataSource({
            'time': [],
            'duty': []
        })
        self.duty_fig = figure(
            title='{}: {}'.format(title, 'Actuator Effort'),
            plot_width=plot_width, plot_height=plot_height,
            y_range=[-255, 255], x_range=self.position_fig.x_range
        )
        self.duty_fig.xaxis.axis_label = 'Time from Start (s)'
        self.duty_fig.xaxis.formatter = DatetimeTickFormatter()
        self.duty_fig.yaxis.axis_label = 'Signed Motor Duty Cycle'
        self.duty_line = self.duty_fig.line(
            x='time', y='duty', source=self.duty_source, line_width=line_width
        )

    def add_position(self, position):
        """Add a point to the plot."""
        self.last_position_time = datetime.datetime.now()
        self.last_position = position
        self.position_source.stream({
            'time': [self.last_position_time],
            'position': [self.last_position]
        }, rollover=self.rollover)

    def add_duty(self, duty):
        """Add a point to the plot."""
        self.last_duty_time = datetime.datetime.now()
        self.last_duty = duty
        self.duty_source.stream({
            'time': [self.last_duty_time],
            'duty': [duty]
        }, rollover=self.rollover)

    def add_position_arrow(self, next_position, slope=0.5, line_width=2):
        """Add an arrow from the last position point to the next position point."""
        self.position_fig.add_layout(annotations.Arrow(
            x_start=self.last_position_time,
            y_start=self.last_position,
            x_end=self.last_position_time + datetime.timedelta(
                milliseconds=next_position * slope
            ),
            y_end=next_position,
            end=arrow_heads.VeeHead(size=10),
            line_width=line_width
        ))

    def add_duty_region(self, start_time, end_time, fill_color, fill_alpha=0.25):
        """Add a shaded region between the two duty cycle times."""
        self.duty_fig.add_layout(annotations.BoxAnnotation(
            left=start_time, right=end_time,
            fill_alpha=fill_alpha, fill_color=fill_color
        ))

    # Implement DocumentLayout

    @property
    def layout(self):
        """Return a document layout element."""
        return self.column_layout


class LinearActuatorPlotter(Plotter, LinearActuatorReceiver):
    """Simple class which prints received serialized messages."""

    def __init__(self, *args, **kwargs):
        """Initialize member variables."""
        super().__init__(*args, **kwargs)

    async def on_linear_actuator(self, state: int) -> None:
        """Receive and handle a LinearActuator response."""
        pass

    async def on_linear_actuator_position(self, position: int) -> None:
        """Receive and handle a LinearActuator/Position response."""
        self.add_position(position)

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
        self.add_duty(duty)

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
