"""Support for real-time plotting of LinearActuator state."""
# Standard imports
import asyncio
import logging

# External imports
from bokeh import layouts
from bokeh.models import ColumnDataSource, callbacks, widgets

# Local package imports
from lhrhost.dashboard import DocumentLayout, DocumentModel
from lhrhost.protocol.linear_actuator.linear_actuator \
    import Receiver as LinearActuatorReceiver

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class PositionLimitsSlider(DocumentModel, LinearActuatorReceiver):
    """Position limits range slider, synchronized across documnts."""

    def __init__(self, linear_actuator_protocol, low=0, high=1023):
        """Initialize member variables."""
        super().__init__(
            widgets.RangeSlider, start=low, end=high, step=1, value=(low, high)
        )
        self.protocol = linear_actuator_protocol.feedback_controller.limits.position
        self.limits_source = ColumnDataSource({'value': []})
        self.limits_source.on_change('data', self._set_limits)
        self.low = low
        self.high = high

    def _disable_slider(self):
        """Disable the slider."""
        def update(slider):
            slider.title = 'Updating position limits...'
            slider.disabled = True
        self.update_docs(update)

    def _enable_slider(self, update_value=True):
        """Enable the slider."""
        new_value = (self.low, self.high)

        def update(slider):
            if update_value:
                slider.value = new_value
            slider.disabled = False
            slider.title = 'Position limits'
        self.update_docs(update)

    def _set_limits(self, attr, old, new):
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
        self._disable_slider()
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

    # Implement DocumentModel

    def make_document_layout(self):
        """Return a new document layout instance."""
        layout = super().make_document_layout()
        # Callback mouseup workaround from https://stackoverflow.com/a/38379136
        layout.callback_policy = 'mouseup'
        layout.callback = callbacks.CustomJS(
            args={'source': self.limits_source},
            code='source.data = {value: [cb_obj.value]}'
        )
        layout.show_value = True
        layout.title = 'Initializing position limits...'
        layout.disabled = True
        return layout

    # Implement LinearActuatorReceiver

    async def on_linear_actuator_feedback_controller_limits_position_low(
        self, position: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Position/Low response."""
        self.low = position
        self._enable_slider()

    async def on_linear_actuator_feedback_controller_limits_position_high(
        self, position: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Position/High response."""
        self.high = position
        self._enable_slider()


class FeedbackControllerPanel(DocumentLayout):
    """Plot of received linear actuator state data."""

    def __init__(self, position_limits_slider):
        """Initialize member variables."""
        super().__init__()

        self.position_limits_slider = position_limits_slider.make_document_layout()

        self._init_controller_widgets()

    def _init_controller_widgets(self):
        """Initialize the linear actuator state plot panel."""
        self.controller_widgets = layouts.widgetbox([
            widgets.Div(text='<h1>Feedback Controller</h1>'),
            self.position_limits_slider
        ])

    # Implement DocumentLayout

    @property
    def layout(self):
        """Return a document layout element."""
        return self.controller_widgets


class FeedbackControllerModel(DocumentModel):
    """Simple class which prints received serialized messages."""

    def __init__(self, linear_actuator_protocol, *args, **kwargs):
        """Initialize member variables."""
        self.position_limits_model = PositionLimitsSlider(
            linear_actuator_protocol, *args, **kwargs
        )
        linear_actuator_protocol.response_receivers.append(self.position_limits_model)
        super().__init__(FeedbackControllerPanel, self.position_limits_model)
