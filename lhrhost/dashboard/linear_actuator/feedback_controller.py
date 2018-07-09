"""Support for real-time plotting of LinearActuator state."""
# Standard imports
import asyncio
import logging

# External imports
from bokeh import layouts
from bokeh.models import widgets

# Local package imports
from lhrhost.dashboard import DocumentLayout, DocumentModel
from lhrhost.dashboard.widgets import Slider
from lhrhost.protocol.linear_actuator.linear_actuator \
    import Receiver as LinearActuatorReceiver

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class PositionLimitsSlider(Slider, LinearActuatorReceiver):
    """Position limits range slider, synchronized across documnts."""

    def __init__(self, linear_actuator_protocol, low=0, high=1023):
        """Initialize member variables."""
        super().__init__(
            'Initializing position limits...',
            slider_widget_class=widgets.RangeSlider,
            start=low, end=high, step=1, value=(low, high)
        )
        self.protocol = linear_actuator_protocol.feedback_controller.limits.position
        self.low = low
        self.high = high

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
                loop.create_task(self.protocol.high.request(self.high))
            if update_low:
                loop.create_task(self.protocol.low.request(self.low))
        else:
            if update_low:
                loop.create_task(self.protocol.low.request(self.low))
            if update_high:
                loop.create_task(self.protocol.high.request(self.high))

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


class LimitsPanel(DocumentLayout):
    """Panel for the feedback controller's limits."""

    def __init__(self, position_limits_slider):
        """Initialize member variables."""
        super().__init__()

        self.position_limits_slider = position_limits_slider.make_document_layout()

        self.controller_widgets = layouts.widgetbox([
            self.position_limits_slider
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
        super().__init__(
            LimitsPanel, self.position_limits_model
        )


class PIDKSlider(Slider):
    """PID gain coefficient slider, synchronized across documnts."""

    def __init__(self, pid_gain_protocol, name, high, step=0.05):
        """Initialize member variables.

        high should be no larger than 32767 / 100.
        """
        super().__init__(
            'Initializing {} gain...'.format(name),
            start=0, end=high, step=step, value=0
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

    def __init__(self, linear_actuator_protocol, high=40):
        """Initialize member variables.

        high should be no larger than 32767 / 100.
        """
        super().__init__(
            linear_actuator_protocol.feedback_controller.pid.kp,
            'proportional', high
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

    def __init__(self, linear_actuator_protocol, high=10):
        """Initialize member variables.

        high should be no larger than 32767 / 100.
        """
        super().__init__(
            linear_actuator_protocol.feedback_controller.pid.kd,
            'derivative', high
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

    def __init__(self, linear_actuator_protocol, high=10):
        """Initialize member variables.

        high should be no larger than 32767 / 100.
        """
        super().__init__(
            linear_actuator_protocol.feedback_controller.pid.ki,
            'integral', high
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

    def __init__(self, linear_actuator_protocol, high=20):
        """Initialize member variables.

        high should be no larger than 32767.
        """
        super().__init__(
            'Initializing PID sampling interval...',
            start=1, end=high, step=1, value=1
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

    def __init__(self, limits_panel, pid_panel, nest_level):
        """Initialize member variables."""
        super().__init__()

        self.limits_panel = limits_panel.make_document_layout()
        self.pid_panel = pid_panel.make_document_layout()

        heading_level = 1 + nest_level
        self.column_layout = layouts.column([
            widgets.Div(text='<h{}>Feedback Controller</h{}>'.format(
                heading_level, heading_level
            )),
            widgets.Tabs(tabs=[
                widgets.Panel(title='Limits', child=self.limits_panel.layout),
                widgets.Panel(title='PID', child=self.pid_panel.layout)
            ])
        ])

    # Implement DocumentLayout

    @property
    def layout(self):
        """Return a document layout element."""
        return self.column_layout


class FeedbackControllerModel(DocumentModel):
    """Parameters panel for the feedback controller, synchronized across documents."""

    def __init__(self, linear_actuator_protocol, *args, nest_level=0, **kwargs):
        """Initialize member variables."""
        self.limits_model = LimitsModel(linear_actuator_protocol, *args, **kwargs)
        self.pid_model = PIDModel(linear_actuator_protocol, *args, **kwargs)
        super().__init__(
            FeedbackControllerPanel, self.limits_model, self.pid_model, nest_level
        )
