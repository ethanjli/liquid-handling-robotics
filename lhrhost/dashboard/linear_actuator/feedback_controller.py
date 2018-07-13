"""Support for real-time plotting of LinearActuator state."""
# Standard imports
import asyncio
import logging
from abc import abstractmethod

# External imports
from bokeh import layouts
from bokeh.models import widgets

# Local package imports
from lhrhost.dashboard import DocumentLayout, DocumentModel
from lhrhost.dashboard.linear_actuator.plots import ClearButton, ErrorsPlotter
from lhrhost.dashboard.widgets import Slider
from lhrhost.protocol.linear_actuator import Receiver as LinearActuatorReceiver
from lhrhost.util.interfaces import InterfaceClass

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class LimitsRangeSlider(Slider, metaclass=InterfaceClass):
    """Limits range slider, synchronized across documents."""

    def __init__(self, limits_protocol, name, low, high, step=1, width=960):
        """Initialize member variables."""
        super().__init__(
            'Initializing {} limits...'.format(name),
            slider_widget_class=widgets.RangeSlider,
            start=low, end=high, step=step, value=(low, high), width=width
        )
        self.name = name
        self.protocol = limits_protocol
        self.low = low
        self.high = high

    @abstractmethod
    async def update_low_limit(self, limit):
        """Issue a request to update the lower limit of the range."""
        pass

    @abstractmethod
    async def update_high_limit(self, limit):
        """Issue a request to update the higher limit of the range."""
        pass

    # Implement Slider

    def on_value_change(self, attr, old, new):
        """Set actuator limits."""
        old_low = self.low
        old_high = self.high
        self.low = int(new['value'][0][0])
        self.high = int(new['value'][0][1])
        # Determine which limits to update
        update_low = False
        update_high = False
        update_high_before_low = False
        update_low = (old_low != self.low)
        update_high = (old_high != self.high)
        # Determine the order in which to update the limits
        if self.low >= old_high:
            update_high_before_low = True
        # Apply the updates
        if update_low or update_high:
            self.disable_slider('Updating position limits...')
        loop = asyncio.get_event_loop()
        if update_high_before_low:
            if update_high:
                loop.create_task(self.update_high_limit(self.high))
            if update_low:
                loop.create_task(self.update_low_limit(self.low))
        else:
            if update_low:
                loop.create_task(self.update_low_limit(self.low))
            if update_high:
                loop.create_task(self.update_high_limit(self.high))


class PositionLimitsSlider(LimitsRangeSlider, LinearActuatorReceiver):
    """Position limits range slider, synchronized across documents."""

    def __init__(self, linear_actuator_protocol, low=0, high=1023, **kwargs):
        """Initialize member variables."""
        super().__init__(
            linear_actuator_protocol.feedback_controller.limits.position,
            'position', low, high, **kwargs
        )

    # Implement RangeSlider

    async def update_low_limit(self, limit):
        """Issue a request to update the lower limit of the range."""
        await self.protocol.low.request(limit)

    async def update_high_limit(self, limit):
        """Issue a request to update the higher limit of the range."""
        await self.protocol.high.request(limit)

    # Implement LinearActuatorReceiver

    async def on_linear_actuator_feedback_controller_limits_position_low(
        self, position: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Position/Low response."""
        self.low = position
        self.enable_slider('Position limits', (self.low, self.high))

    async def on_linear_actuator_feedback_controller_limits_position_high(
        self, position: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Position/High response."""
        self.high = position
        self.enable_slider('Position limits', (self.low, self.high))


class MotorForwardsLimitsSlider(LimitsRangeSlider, LinearActuatorReceiver):
    """Motor forwards duty limits range slider, synchronized across documents."""

    def __init__(self, linear_actuator_protocol, **kwargs):
        """Initialize member variables."""
        super().__init__(
            linear_actuator_protocol.feedback_controller.limits.motor.forwards,
            'motor forwards duty cycle magnitude', 0, 255, step=5, **kwargs
        )

    # Implement RangeSlider

    async def update_low_limit(self, limit):
        """Issue a request to update the lower limit of the range."""
        await self.protocol.low.request(limit)

    async def update_high_limit(self, limit):
        """Issue a request to update the higher limit of the range."""
        await self.protocol.high.request(limit)

    # Implement LinearActuatorReceiver

    async def on_linear_actuator_feedback_controller_limits_motor_forwards_low(
        self, position: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Forwards/Low response."""
        self.low = position
        self.enable_slider(
            'Motor forwards duty cycle magnitude limits', (self.low, self.high)
        )

    async def on_linear_actuator_feedback_controller_limits_motor_forwards_high(
        self, position: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Forwards/High response."""
        self.high = position
        self.enable_slider(
            'Motor forwards duty cycle magnitude limits', (self.low, self.high)
        )


class MotorBackwardsLimitsSlider(LimitsRangeSlider, LinearActuatorReceiver):
    """Motor backwards duty limits range slider, synchronized across documents."""

    def __init__(self, linear_actuator_protocol, **kwargs):
        """Initialize member variables."""
        super().__init__(
            linear_actuator_protocol.feedback_controller.limits.motor.backwards,
            'motor backwards duty cycle magnitude', 0, 255, step=5, **kwargs
        )

    # Implement RangeSlider

    async def update_low_limit(self, limit):
        """Issue a request to update the lower limit of the range."""
        await self.protocol.low.request(-1 * limit)

    async def update_high_limit(self, limit):
        """Issue a request to update the higher limit of the range."""
        await self.protocol.high.request(-1 * limit)

    # Implement LinearActuatorReceiver

    async def on_linear_actuator_feedback_controller_limits_motor_backwards_low(
        self, position: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Backwards/Low response."""
        self.low = -1 * position
        self.enable_slider(
            'Motor backwards duty cycle magnitude limits', (self.low, self.high)
        )

    async def on_linear_actuator_feedback_controller_limits_motor_backwards_high(
        self, position: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Backwards/High response."""
        self.high = -1 * position
        self.enable_slider(
            'Motor backwards duty cycle magnitude limits', (self.low, self.high)
        )


class LimitsPanel(DocumentLayout):
    """Panel for the feedback controller's limits."""

    def __init__(
        self, position_limits_slider,
        motor_forwards_limits_slider, motor_backwards_limits_slider
    ):
        """Initialize member variables."""
        super().__init__()

        self.position_limits_slider = position_limits_slider.make_document_layout()
        self.motor_forwards_limits_slider = \
            motor_forwards_limits_slider.make_document_layout()
        self.motor_backwards_limits_slider = \
            motor_backwards_limits_slider.make_document_layout()

        self.controller_widgets = layouts.widgetbox([
            self.position_limits_slider,
            self.motor_forwards_limits_slider,
            self.motor_backwards_limits_slider
        ])

    # Implement DocumentLayout

    @property
    def layout(self):
        """Return a document layout element."""
        return self.controller_widgets


class LimitsModel(DocumentModel):
    """Panel for the feedback controller's limits, synchronized across documents."""

    def __init__(self, linear_actuator_protocol, *args, **kwargs):
        """Initialize member variables."""
        self.position_limits_model = PositionLimitsSlider(
            linear_actuator_protocol, *args, **kwargs
        )
        linear_actuator_protocol.response_receivers.append(self.position_limits_model)
        self.motor_forwards_limits_model = MotorForwardsLimitsSlider(
            linear_actuator_protocol, *args, **kwargs
        )
        linear_actuator_protocol.response_receivers.append(self.motor_forwards_limits_model)
        self.motor_backwards_limits_model = MotorBackwardsLimitsSlider(
            linear_actuator_protocol, *args, **kwargs
        )
        linear_actuator_protocol.response_receivers.append(self.motor_backwards_limits_model)
        super().__init__(
            LimitsPanel,
            self.position_limits_model,
            self.motor_forwards_limits_model,
            self.motor_backwards_limits_model
        )


class TimeoutSlider(Slider):
    """Timeout slider, synchronized across documnts."""

    def __init__(self, timeout_protocol, name, low=0, high=2000, step=10, width=960):
        """Initialize member variables.

        high should be no larger than 32767.
        """
        super().__init__(
            'Initializing {} timeout...'.format(name),
            start=0, end=high, step=step, value=0, width=width
        )
        self.protocol = timeout_protocol
        self.name = name
        self.value = 0

    # Implement Slider

    def on_value_change(self, attr, old, new):
        """Set actuator limits."""
        old_value = self.value
        self.value = new['value'][0]
        # Apply the updates
        if old_value != self.value:
            self.disable_slider('Updating {} timeout...'.format(self.name))
            loop = asyncio.get_event_loop()
            loop.create_task(self.protocol.request(int(self.value)))


class StallProtectorTimeoutSlider(TimeoutSlider, LinearActuatorReceiver):
    """Stall protector timeout slider, synchronized across documnts."""

    def __init__(self, linear_actuator_protocol, low=0, high=500, **kwargs):
        """Initialize member variables.

        high should be no larger than 32767.
        """
        super().__init__(
            linear_actuator_protocol.motor.stall_protector_timeout,
            'motor stall protector', low=low, high=high, **kwargs
        )

    # Implement LinearActuatorReceiver

    async def on_linear_actuator_motor_stall_protector_timeout(
        self, timeout: int
    ) -> None:
        """Receive and handle a LA/Motor/StallProtectorTimeout response."""
        self.value = timeout
        self.enable_slider('Motor stall protector timeout (ms)', self.value)


class TimerTimeoutSlider(TimeoutSlider, LinearActuatorReceiver):
    """Timer timeout slider, synchronized across documnts."""

    def __init__(self, linear_actuator_protocol, high=10000, **kwargs):
        """Initialize member variables.

        high should be no larger than 32767.
        """
        super().__init__(
            linear_actuator_protocol.motor.timer_timeout,
            'motion timer', high=high, step=50, **kwargs
        )

    # Implement LinearActuatorReceiver

    async def on_linear_actuator_motor_timer_timeout(
        self, timeout: int
    ) -> None:
        """Receive and handle a LA/Motor/TimerTimeout response."""
        self.value = timeout
        self.enable_slider('Motion timer timeout (ms)', self.value)


class ConvergenceTimeoutSlider(TimeoutSlider, LinearActuatorReceiver):
    """Convergence timeout slider, synchronized across documnts."""

    def __init__(self, linear_actuator_protocol, high=500, **kwargs):
        """Initialize member variables.

        high should be no larger than 32767.
        """
        super().__init__(
            linear_actuator_protocol.feedback_controller.convergence_timeout,
            'convergence detector', high=high, step=10, **kwargs
        )

    # Implement LinearActuatorReceiver

    async def on_linear_actuator_feedback_controller_convergence_timeout(
        self, timeout: int
    ) -> None:
        """Receive and handle a LA/FeedbackController/ConvergenceTimeout response."""
        self.value = timeout
        self.enable_slider('Convergence detector timeout (ms)', self.value)


class TimeoutsPanel(DocumentLayout):
    """Panel for the feedback controller's timeouts."""

    def __init__(
        self, stall_timeout_slider, timer_timeout_slider, convegence_timeout_slider
    ):
        """Initialize member variables."""
        super().__init__()

        self.stall_timeout_slider = stall_timeout_slider.make_document_layout()
        self.timer_timeout_slider = timer_timeout_slider.make_document_layout()
        self.convegence_timeout_slider = \
            convegence_timeout_slider.make_document_layout()

        self.controller_widgets = layouts.widgetbox([
            self.stall_timeout_slider, self.timer_timeout_slider,
            self.convegence_timeout_slider
        ])

    # Implement DocumentLayout

    @property
    def layout(self):
        """Return a document layout element."""
        return self.controller_widgets


class TimeoutsModel(DocumentModel):
    """Panel for the feedback controller's limits, synchronized across documents."""

    def __init__(self, linear_actuator_protocol, *args, **kwargs):
        """Initialize member variables."""
        self.stall_timeout_model = StallProtectorTimeoutSlider(
            linear_actuator_protocol, *args, **kwargs
        )
        self.timer_timeout_model = TimerTimeoutSlider(
            linear_actuator_protocol, *args, **kwargs
        )
        self.convergence_timeout_model = ConvergenceTimeoutSlider(
            linear_actuator_protocol, *args, **kwargs
        )
        linear_actuator_protocol.response_receivers.append(self.stall_timeout_model)
        linear_actuator_protocol.response_receivers.append(self.timer_timeout_model)
        linear_actuator_protocol.response_receivers.append(
            self.convergence_timeout_model
        )
        super().__init__(
            TimeoutsPanel,
            self.stall_timeout_model, self.timer_timeout_model,
            self.convergence_timeout_model
        )


class PIDKSlider(Slider):
    """PID gain coefficient slider, synchronized across documnts."""

    def __init__(self, pid_gain_protocol, name, high, step=0.01, width=960):
        """Initialize member variables.

        high should be no larger than 32767 / 100.
        """
        super().__init__(
            'Initializing {} gain...'.format(name),
            start=0, end=high, step=step, value=0, width=width
        )
        self.protocol = pid_gain_protocol
        self.name = name
        self.value = 0

    # Implement Slider

    def on_value_change(self, attr, old, new):
        """Set actuator limits."""
        old_value = self.value
        self.value = new['value'][0]
        # Apply the updates
        if old_value != self.value:
            self.disable_slider('Updating {} gain...'.format(self.name))
            loop = asyncio.get_event_loop()
            loop.create_task(self.protocol.request(int(self.value * 100)))


class PIDKpSlider(PIDKSlider, LinearActuatorReceiver):
    """PID Kp slider, synchronized across documnts."""

    def __init__(self, linear_actuator_protocol, high=50, **kwargs):
        """Initialize member variables.

        high should be no larger than 32767 / 100.
        """
        super().__init__(
            linear_actuator_protocol.feedback_controller.pid.kp,
            'proportional', high, step=0.5, **kwargs
        )

    # Implement LinearActuatorReceiver

    async def on_linear_actuator_feedback_controller_pid_kp(
        self, coefficient: int
    ) -> None:
        """Receive and handle a LA/FC/PID/Kp response."""
        self.value = coefficient / 100
        self.enable_slider('Proportional gain', self.value)


class PIDKdSlider(PIDKSlider, LinearActuatorReceiver):
    """PID Kd slider, synchronized across documnts."""

    def __init__(self, linear_actuator_protocol, high=2, **kwargs):
        """Initialize member variables.

        high should be no larger than 32767 / 100.
        """
        super().__init__(
            linear_actuator_protocol.feedback_controller.pid.kd,
            'derivative', high, step=0.05, **kwargs
        )

    # Implement LinearActuatorReceiver

    async def on_linear_actuator_feedback_controller_pid_kd(
        self, coefficient: int
    ) -> None:
        """Receive and handle a LA/FC/PID/Kd response."""
        self.value = coefficient / 100
        self.enable_slider('Derivative gain', self.value)


class PIDKiSlider(PIDKSlider, LinearActuatorReceiver):
    """PID Ki slider, synchronized across documnts."""

    def __init__(self, linear_actuator_protocol, high=4, **kwargs):
        """Initialize member variables.

        high should be no larger than 32767 / 100.
        """
        super().__init__(
            linear_actuator_protocol.feedback_controller.pid.ki,
            'integral', high, **kwargs
        )

    # Implement LinearActuatorReceiver

    async def on_linear_actuator_feedback_controller_pid_ki(
        self, coefficient: int
    ) -> None:
        """Receive and handle a LA/FC/PID/Ki response."""
        self.value = coefficient / 100
        self.enable_slider('Integral gain', self.value)


class PIDSampleIntervalSlider(Slider, LinearActuatorReceiver):
    """PID sample interval slider, synchronized across documents.

    For some reason the peripheral's implementation of the sample interval channel
    doesn't work right now.
    """

    def __init__(self, linear_actuator_protocol, high=20, width=960, **kwargs):
        """Initialize member variables.

        high should be no larger than 32767.
        """
        super().__init__(
            'Initializing PID sampling interval...',
            start=1, end=high, step=1, value=1, width=width, **kwargs
        )
        self.protocol = \
            linear_actuator_protocol.feedback_controller.pid.sample_interval
        self.value = 1

    # Implement Slider

    def on_value_change(self, attr, old, new):
        """Set actuator limits."""
        old_value = self.value
        self.value = int(new['value'][0])
        # Apply the updates
        if old_value != self.value:
            self.disable_slider('Updating PID sampling interval...')
            loop = asyncio.get_event_loop()
            loop.create_task(self.protocol.request(self.value))

    # Implement LinearActuatorReceiver

    async def on_linear_actuator_feedback_controller_pid_sample_interval(
        self, interval: int
    ) -> None:
        """Receive and handle a LA/FC/PID/SampleInterval response."""
        self.value = interval
        self.enable_slider('PID sampling interval', self.value)


class PIDPanel(DocumentLayout):
    """Panel for the feedback controller's PID controller."""

    def __init__(
        self, pid_kp_slider, pid_kd_slider, pid_ki_slider,
        # pid_sample_interval_slider
    ):
        """Initialize member variables."""
        super().__init__()

        self.pid_kp_slider = pid_kp_slider.make_document_layout()
        self.pid_kd_slider = pid_kd_slider.make_document_layout()
        self.pid_ki_slider = pid_ki_slider.make_document_layout()
        # self.pid_sample_interval_slider = \
        #     pid_sample_interval_slider.make_document_layout()

        self.controller_widgets = layouts.widgetbox([
            self.pid_kp_slider, self.pid_kd_slider, self.pid_ki_slider,
            # self.pid_sample_interval_slider
        ])

    # Implement DocumentLayout

    @property
    def layout(self):
        """Return a document layout element."""
        return self.controller_widgets


class PIDModel(DocumentModel):
    """Panel for the feedback controller's limits, synchronized across documents."""

    def __init__(self, linear_actuator_protocol, *args, **kwargs):
        """Initialize member variables."""
        self.pid_kp_model = PIDKpSlider(linear_actuator_protocol, *args, **kwargs)
        self.pid_kd_model = PIDKdSlider(linear_actuator_protocol, *args, **kwargs)
        self.pid_ki_model = PIDKiSlider(linear_actuator_protocol, *args, **kwargs)
        # self.pid_sample_interval_model = \
        #     PIDSampleIntervalSlider(linear_actuator_protocol, *args, **kwargs)
        linear_actuator_protocol.response_receivers.append(self.pid_kp_model)
        linear_actuator_protocol.response_receivers.append(self.pid_kd_model)
        linear_actuator_protocol.response_receivers.append(self.pid_ki_model)
        # linear_actuator_protocol.response_receivers.append(
        #     self.pid_sample_interval_model
        # )
        super().__init__(
            PIDPanel,
            self.pid_kp_model, self.pid_kd_model, self.pid_ki_model,
            # self.pid_sample_interval_model
        )


class FeedbackControllerPanel(DocumentLayout):
    """Parameters panel for the feedback controller."""

    def __init__(
        self, limits_panel, timeouts_panel, pid_panel,
        errors_plotter, errors_plotter_clear_button, title, nest_level, width=960
    ):
        """Initialize member variables."""
        super().__init__()

        self.limits_panel = limits_panel.make_document_layout()
        self.timeouts_panel = timeouts_panel.make_document_layout()
        self.pid_panel = pid_panel.make_document_layout()
        self.errors_plotter = errors_plotter.make_document_layout()
        self.errors_plotter_clear_button = \
            errors_plotter_clear_button.make_document_layout()

        heading_level = 1 + nest_level
        column = []
        if title:
            column += [
                layouts.widgetbox([
                    widgets.Div(text='<h{}>Feedback Controller</h{}>'.format(
                        heading_level, heading_level
                    ))
                ])
            ]
        column += [
            widgets.Tabs(tabs=[
                widgets.Panel(title='Limits', child=self.limits_panel.layout),
                widgets.Panel(title='Timeouts', child=self.timeouts_panel.layout),
                widgets.Panel(title='PID', child=self.pid_panel.layout),
                widgets.Panel(title='Errors', child=layouts.column([
                    self.errors_plotter.layout,
                    self.errors_plotter_clear_button
                ]))
            ], width=width)
        ]
        self.column_layout = layouts.column(column)

    # Implement DocumentLayout

    @property
    def layout(self):
        """Return a document layout element."""
        return self.column_layout

    def initialize_doc(self, doc, as_root=False):
        """Initialize the provided document."""
        super().initialize_doc(doc, as_root)
        self.errors_plotter.initialize_doc(self.document)


class FeedbackControllerModel(DocumentModel):
    """Parameters panel for the feedback controller, synchronized across documents."""

    def __init__(self, linear_actuator_protocol, *args, nest_level=0, title=None, **kwargs):
        """Initialize member variables."""
        self.limits_model = LimitsModel(linear_actuator_protocol, *args, **kwargs)
        self.timeouts_model = TimeoutsModel(linear_actuator_protocol, *args, **kwargs)
        self.pid_model = PIDModel(linear_actuator_protocol, *args, **kwargs)
        self.errors_plotter = ErrorsPlotter(*args, **kwargs)
        self.errors_plotter_clear_button = ClearButton(self.errors_plotter)
        if title is None:
            title = 'Feedback Controller'
        super().__init__(
            FeedbackControllerPanel, self.limits_model, self.timeouts_model,
            self.pid_model, self.errors_plotter, self.errors_plotter_clear_button,
            title, nest_level, **kwargs
        )
