"""Support for real-time plotting of LinearActuator state."""
# Standard imports
import datetime
import logging

# External imports
from bokeh import layouts
from bokeh.models import (
    ColumnDataSource, DatetimeTickFormatter, annotations, arrow_heads, widgets
)
from bokeh.plotting import figure

# Local package imports
from lhrhost.dashboard import DocumentLayout, DocumentModel
from lhrhost.protocol.linear_actuator.linear_actuator \
    import Receiver as LinearActuatorReceiver

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class PositionPlot(DocumentLayout):
    """Plot of received linear actuator position data."""

    def __init__(
        self, title, rollover=750,
        plot_width=960, plot_height=320, line_width=2
    ):
        """Initialize member variables."""
        super().__init__()
        self.rollover = rollover
        self._init_position_plot(title, plot_width, plot_height, line_width)
        self.last_position_time = None
        self.last_position = None
        self.last_region = None

    def _init_position_plot(self, title, plot_width, plot_height, line_width):
        """Initialize member variables for position plotting."""
        self.position_source = ColumnDataSource({
            'time': [],
            'position': []
        })
        self.position_fig = figure(
            title=title, plot_width=plot_width, plot_height=plot_height
        )
        self.position_fig.xaxis.axis_label = 'Time from Start (s)'
        self.position_fig.xaxis.formatter = DatetimeTickFormatter()
        self.position_fig.yaxis.axis_label = 'Position'
        self.position_line = self.position_fig.line(
            x='time', y='position', source=self.position_source, line_width=line_width
        )

    def add_position(self, position):
        """Add a point to the plot."""
        self.last_position_time = datetime.datetime.now()
        self.last_position = position
        self.position_source.stream({
            'time': [self.last_position_time],
            'position': [self.last_position]
        }, rollover=self.rollover)

    def clear(self):
        """Clear plot data."""
        for arrow in self.position_fig.select(name='arrow'):
            self.position_fig.renderers.remove(arrow)
        for region in self.position_fig.select(name='region'):
            self.position_fig.renderers.remove(region)
        self.position_source.data = {'time': [], 'position': []}
        if self.last_region is not None:
            self.start_limits_region(
                self.last_region.bottom, self.last_region.top,
                start_time=self.last_region.left,
                fill_color=self.last_region.fill_color,
                fill_alpha=self.last_region.fill_alpha
            )

    def add_arrow(self, next_position, slope=1, line_width=2):
        """Add an arrow from the last position point to the next position point."""
        if self.last_position_time is None or self.last_position is None:
            logger.warn('Could not add position arrow from unknown last position!')
            return
        self.position_fig.add_layout(annotations.Arrow(
            x_start=self.last_position_time,
            y_start=self.last_position,
            x_end=self.last_position_time + datetime.timedelta(
                milliseconds=abs(next_position - self.last_position) / slope
            ),
            y_end=next_position,
            end=arrow_heads.VeeHead(size=10),
            line_width=line_width,
            name='arrow'
        ))

    def start_limits_region(
        self, low, high, start_time=None, fill_color='gray', fill_alpha=0.25
    ):
        """Start a position region."""
        if start_time is None:
            start_time = datetime.datetime.now()
        self.last_region = annotations.BoxAnnotation(
            left=start_time, bottom=low, top=high,
            fill_color=fill_color, fill_alpha=fill_alpha,
            name='region'
        )
        self.position_fig.add_layout(self.last_region)

    def end_limits_region(self, end_time=None):
        """End position region."""
        if self.last_region is None:
            return
        if end_time is None:
            end_time = datetime.datetime.now()
        self.last_region.right = end_time

    # Implement DocumentLayout

    @property
    def layout(self):
        """Return a document layout element."""
        return self.position_fig


class PositionPlotter(DocumentModel, LinearActuatorReceiver):
    """Linear actuator position plotter, synchronized across documents."""

    def __init__(self, *args, **kwargs):
        """Initialize member variables."""
        super().__init__(PositionPlot, *args, **kwargs)
        self.last_position_time = None
        self.last_position = None
        self.position_limit_low = None
        self.position_limit_high = None

    def clear(self):
        """Clear plot data."""
        self.update_docs(lambda plot: plot.clear())

    def add_arrow(self, *args, **kwargs):
        """Add an arrow from the most recent position point to the next position point."""
        self.update_docs(lambda plot: plot.add_arrow(*args, **kwargs))

    def update_limits_region(self):
        """Update the limits region."""
        if self.position_limit_low is None or self.position_limit_high is None:
            return
        self.update_docs(lambda plot: plot.end_limits_region())
        self.update_docs(lambda plot: plot.start_limits_region(
            self.position_limit_low, self.position_limit_high
        ))

    # Implement LinearActuatorReceiver

    async def on_linear_actuator_position(self, position: int) -> None:
        """Receive and handle a LinearActuator/Position response."""
        self.last_position_time = datetime.datetime.now()
        self.last_position = position
        self.update_docs(lambda plot: plot.add_position(position))

    async def on_linear_actuator_feedback_controller_limits_position_low(
        self, position: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Position/Low response."""
        self.position_limit_low = position
        self.update_limits_region()

    async def on_linear_actuator_feedback_controller_limits_position_high(
        self, position: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Position/High response."""
        self.position_limit_high = position
        self.update_limits_region()


class DutyPlot(DocumentLayout):
    """Plot of received linear actuator motor duty cycle data."""

    def __init__(
        self, title, rollover=750,
        plot_width=960, plot_height=320, line_width=2
    ):
        """Initialize member variables."""
        super().__init__()
        self.rollover = rollover
        self._init_duty_plot(title, plot_width, plot_height, line_width)
        self.duty_state_region_start_time = None
        self.last_limits_regions = {
            'forwards': None,
            'backwards': None
        }

    def _init_duty_plot(self, title, plot_width, plot_height, line_width):
        """Initialize member variables for motor duty cycle plotting."""
        self.duty_source = ColumnDataSource({
            'time': [],
            'duty': []
        })
        self.duty_fig = figure(
            title=title, plot_width=plot_width, plot_height=plot_height,
            y_range=[-255, 255]
        )
        self.duty_fig.xaxis.axis_label = 'Time from Start (s)'
        self.duty_fig.xaxis.formatter = DatetimeTickFormatter()
        self.duty_fig.yaxis.axis_label = 'Signed Motor Duty Cycle'
        self.duty_line = self.duty_fig.line(
            x='time', y='duty', source=self.duty_source, line_width=line_width
        )

    def add_duty(self, duty):
        """Add a point to the plot."""
        self.duty_source.stream({
            'time': [datetime.datetime.now()],
            'duty': [duty]
        }, rollover=self.rollover)

    def clear(self):
        """Clear plot data."""
        for region in self.duty_fig.select(name='region'):
            self.duty_fig.renderers.remove(region)
        self.duty_source.data = {'time': [], 'duty': []}
        for (direction, region) in self.last_limits_regions.items():
            if region is not None:
                self.start_limits_region(
                    direction, region.bottom, region.top, start_time=region.left,
                    fill_color=region.fill_color, fill_alpha=region.fill_alpha
                )

    def add_state_region(self, fill_color, start_time=None, end_time=None, fill_alpha=0.25):
        """Add a shaded region between the two duty cycle times."""
        if start_time is None:
            start_time = self.duty_state_region_start_time
        if start_time is None:
            logger.warn('Could not add duty region from unspecified start time!')
            return
        if end_time is None:
            end_time = datetime.datetime.now()
        self.duty_fig.add_layout(annotations.BoxAnnotation(
            left=start_time, right=end_time,
            fill_alpha=fill_alpha, fill_color=fill_color,
            name='region'
        ))

    def start_state_region(self):
        """Start a duty cycle region."""
        self.duty_state_region_start_time = datetime.datetime.now()

    def start_limits_region(
        self, direction, low, high, start_time=None,
        fill_color='gray', fill_alpha=0.25
    ):
        """Start a duty cycle lmits region."""
        if start_time is None:
            start_time = datetime.datetime.now()
        self.last_limits_regions[direction] = annotations.BoxAnnotation(
            left=start_time, bottom=low, top=high,
            fill_color=fill_color, fill_alpha=fill_alpha,
            name='region'
        )
        self.duty_fig.add_layout(self.last_limits_regions[direction])

    def end_limits_region(self, direction, end_time=None):
        """End duty cycle limits region."""
        if self.last_limits_regions[direction] is None:
            return
        if end_time is None:
            end_time = datetime.datetime.now()
        self.last_limits_regions[direction].right = end_time

    # Implement DocumentLayout

    @property
    def layout(self):
        """Return a document layout element."""
        return self.duty_fig


class DutyPlotter(DocumentModel, LinearActuatorReceiver):
    """Linear actuator motor duty cycle plotter, synchronized across documents."""

    def __init__(self, *args, **kwargs):
        """Initialize member variables."""
        super().__init__(DutyPlot, *args, **kwargs)
        self.last_duty_time = None
        self.last_duty = None
        self.motor_limit_low = {
            'forwards': None,
            'backwards': None
        }
        self.motor_limit_high = {
            'forwards': None,
            'backwards': None
        }

    def clear(self):
        """Clear plot data."""
        self.update_docs(lambda plot: plot.clear())

    def add_state_region(self, *args, **kwargs):
        """Add an arrow from the last position point to the next position point."""
        self.update_docs(lambda plot: plot.add_state_region(*args, **kwargs))

    def start_state_region(self):
        """Add an arrow from the last position point to the next position point."""
        self.update_docs(lambda plot: plot.start_state_region())

    def update_limits_region(self, direction):
        """Update the limits region."""
        if (
                self.motor_limit_low[direction] is None or
                self.motor_limit_high[direction] is None
        ):
            return
        self.update_docs(lambda plot: plot.end_limits_region(direction))
        self.update_docs(lambda plot: plot.start_limits_region(
            direction,
            self.motor_limit_low[direction],
            self.motor_limit_high[direction]
        ))

    # Implement LinearActuatorReceiver

    async def on_linear_actuator_motor(self, duty: int) -> None:
        """Receive and handle a LinearActuator/Motor response."""
        self.last_duty_time = datetime.datetime.now()
        self.last_duty = duty
        self.update_docs(lambda plot: plot.add_duty(duty))

    async def on_linear_actuator_feedback_controller_limits_motor_forwards_low(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Forwards/Low response."""
        self.motor_limit_low['forwards'] = duty
        self.update_limits_region('forwards')

    async def on_linear_actuator_feedback_controller_limits_motor_forwards_high(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Forwards/High response."""
        self.motor_limit_high['forwards'] = duty
        self.update_limits_region('forwards')

    async def on_linear_actuator_feedback_controller_limits_motor_backwards_low(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Backwards/Low response."""
        self.motor_limit_low['backwards'] = duty
        self.update_limits_region('backwards')

    async def on_linear_actuator_feedback_controller_limits_motor_backwards_high(
        self, duty: int
    ) -> None:
        """Receive and handle a LA/FC/Limits/Motor/Backwards/High response."""
        self.motor_limit_high['backwards'] = duty
        self.update_limits_region('backwards')


class LinearActuatorPlot(DocumentLayout):
    """Plot of received linear actuator state data."""

    def __init__(self, position_plotter, duty_plotter, title, nest_level):
        """Initialize member variables."""
        super().__init__()

        self.position_plot = position_plotter.make_document_layout()
        self.duty_plot = duty_plotter.make_document_layout()
        self.duty_plot.duty_fig.x_range = self.position_plot.position_fig.x_range

        self._init_controller_widgets(title, nest_level)
        self.column_layout = layouts.column([
            self.controller_widgets,
            self.position_plot.layout,
            self.duty_plot.layout
        ])

    def _init_controller_widgets(self, title, nest_level):
        """Initialize the linear actuator state plot panel."""
        heading_level = 1 + nest_level
        self.controller_widgets = layouts.widgetbox([
            widgets.Div(text='<h{}>{}</h{}>'.format(
                heading_level, title, heading_level
            ))
        ])

    # Implement DocumentLayout

    @property
    def layout(self):
        """Return a document layout element."""
        return self.column_layout

    def initialize_doc(self, doc, as_root=False):
        """Initialize the provided document."""
        super().initialize_doc(doc, as_root)
        self.position_plot.initialize_doc(self.document)
        self.duty_plot.initialize_doc(self.document)


class LinearActuatorPlotter(DocumentModel):
    """Simple class which prints received serialized messages."""

    def __init__(self, linear_actuator_protocol, *args, nest_level=0, **kwargs):
        """Initialize member variables."""
        self.position_plotter = PositionPlotter('Actuator Position', *args, **kwargs)
        self.duty_plotter = DutyPlotter('Actuator Effort', *args, **kwargs)
        linear_actuator_protocol.response_receivers.append(self.position_plotter)
        linear_actuator_protocol.response_receivers.append(self.duty_plotter)
        if nest_level == 0:
            title = linear_actuator_protocol.channel_path
        else:
            title = 'State Plots'
        super().__init__(
            LinearActuatorPlot, self.position_plotter, self.duty_plotter,
            title, nest_level=nest_level
        )
