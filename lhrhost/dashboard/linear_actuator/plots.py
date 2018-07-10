"""Support for real-time plotting of LinearActuator state."""
# Standard imports
import asyncio
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
from lhrhost.dashboard.widgets import Button
from lhrhost.protocol.linear_actuator.linear_actuator \
    import Receiver as LinearActuatorReceiver

# External imports
import numpy as np

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ClearButton(Button):
    """Plotter clear button, synchronized across documents."""

    def __init__(self, *plotters):
        """Initialize member variables."""
        super().__init__(label='Clear plot')
        self.plotters = plotters

    # Implement Button

    def on_click(self):
        """Handle a button click event."""
        for plotter in self.plotters:
            plotter.clear()


class PositionPlot(DocumentLayout):
    """Plot of received linear actuator position data."""

    def __init__(
        self, title, rollover=750, width=960, height=320, line_width=2
    ):
        """Initialize member variables."""
        super().__init__()
        self.rollover = rollover
        self._init_position_plot(title, width, height, line_width)
        self.plotting = True
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
        if not self.plotting:
            return
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

    def start_plotting(self):
        """Start plotting data."""
        self.plotting = True

    def stop_plotting(self):
        """Stop plotting data."""
        self.plotting = False

    def add_arrow(self, next_position, slope=1, line_width=2):
        """Add an arrow from the last position point to the next position point."""
        if not self.plotting:
            return
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
        if not self.plotting:
            return
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
        if not self.plotting:
            return
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

    def start_plotting(self):
        """Start plotting data."""
        self.update_docs(lambda plot: plot.start_plotting())

    def stop_plotting(self):
        """Stop plotting data."""
        self.update_docs(lambda plot: plot.stop_plotting())

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
        self, title, rollover=750, width=960, height=320, line_width=2
    ):
        """Initialize member variables."""
        super().__init__()
        self.rollover = rollover
        self._init_duty_plot(title, width, height, line_width)
        self.plotting = True
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
        if not self.plotting:
            return
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

    def start_plotting(self):
        """Start plotting data."""
        self.plotting = True

    def stop_plotting(self):
        """Stop plotting data."""
        self.plotting = False

    def add_state_region(self, fill_color, start_time=None, end_time=None, fill_alpha=0.25):
        """Add a shaded region between the two duty cycle times."""
        if not self.plotting:
            return
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
        if not self.plotting:
            return
        self.duty_state_region_start_time = datetime.datetime.now()

    def start_limits_region(
        self, direction, low, high, start_time=None,
        fill_color='gray', fill_alpha=0.25
    ):
        """Start a duty cycle lmits region."""
        if not self.plotting:
            return
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
        if not self.plotting:
            return
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

    def start_plotting(self):
        """Start plotting data."""
        self.update_docs(lambda plot: plot.start_plotting())

    def stop_plotting(self):
        """Stop plotting data."""
        self.update_docs(lambda plot: plot.stop_plotting())

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


class ToggleStatePlottingButton(Button):
    """Linear actuator plotter functionality toggle, synchronized across documents."""

    def __init__(self, linear_actuator_protocol, plotters, plotting_interval=20):
        """Initialize member variables."""
        super().__init__(label='Start Plotting')
        self.protocol = linear_actuator_protocol
        self.plotters = plotters
        self.plotting = False
        self.interval = plotting_interval

    async def toggle_plotting(self):
        """Toggle plotting."""
        if self.plotting:
            await self.stop_plotting()
        else:
            await self.start_plotting()

    async def start_plotting(self):
        """Start plotting if it hasn't already started."""
        if self.plotting:
            return
        await self.protocol.position.notify.change_only.request(0)
        await self.protocol.position.notify.interval.request(self.interval)
        await self.protocol.motor.notify.change_only.request(0)
        await self.protocol.motor.notify.interval.request(self.interval)
        await self.protocol.position.notify.request(2)
        await self.protocol.motor.notify.request(2)
        self.plotting = True
        for plotter in self.plotters:
            plotter.start_plotting()
        self.enable_button('Stop plotting')

    async def stop_plotting(self):
        """Stop plotting if it hasn't already stopped."""
        if not self.plotting:
            return
        await self.protocol.position.notify.request(0)
        await self.protocol.motor.notify.request(0)
        self.plotting = False
        for plotter in self.plotters:
            plotter.stop_plotting()
        self.enable_button('Start plotting')

    # Implement Button

    def on_click(self):
        """Handle a button click event."""
        label = 'Stopping plotting...' if self.plotting else 'Stopping plotting'
        self.disable_button(label)
        asyncio.get_event_loop().create_task(self.toggle_plotting())


class LinearActuatorPlot(DocumentLayout):
    """Plot of received linear actuator state data."""

    def __init__(
        self, position_plotter, duty_plotter, clear_button, toggle_button,
        title, nest_level
    ):
        """Initialize member variables."""
        super().__init__()

        self.position_plot = position_plotter.make_document_layout()
        self.duty_plot = duty_plotter.make_document_layout()
        self.duty_plot.duty_fig.x_range = self.position_plot.position_fig.x_range
        self.clear_button = clear_button.make_document_layout()
        self.toggle_button = toggle_button.make_document_layout()

        heading_level = 1 + nest_level
        column = []
        if title:
            column += [
                layouts.widgetbox([
                    widgets.Div(text='<h{}>{}</h{}>'.format(
                        heading_level, title, heading_level
                    ))
                ])
            ]
        column += [
            layouts.row([
                layouts.widgetbox([self.clear_button]),
                layouts.widgetbox([self.toggle_button])
            ]),
            self.position_plot.layout,
            self.duty_plot.layout
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
        self.position_plot.initialize_doc(self.document)
        self.duty_plot.initialize_doc(self.document)


class LinearActuatorPlotter(DocumentModel):
    """Plot of received linear actuator state data, synchronized across documents."""

    def __init__(
        self, linear_actuator_protocol, *args, nest_level=0, title=None, **kwargs
    ):
        """Initialize member variables."""
        self.position_plotter = PositionPlotter('Actuator Position', *args, **kwargs)
        self.duty_plotter = DutyPlotter('Actuator Effort', *args, **kwargs)
        self.clear_button = ClearButton(self.position_plotter, self.duty_plotter)
        self.toggler = ToggleStatePlottingButton(
            linear_actuator_protocol, [self.position_plotter, self.duty_plotter]
        )
        linear_actuator_protocol.response_receivers.append(self.position_plotter)
        linear_actuator_protocol.response_receivers.append(self.duty_plotter)
        if title is None:
            if nest_level == 0:
                title = linear_actuator_protocol.channel_path
            else:
                title = 'State Plots'
        super().__init__(
            LinearActuatorPlot, self.position_plotter, self.duty_plotter,
            self.clear_button, self.toggler, title, nest_level=nest_level
        )


class ErrorsPlot(DocumentLayout):
    """Plot of errors in converged positions from setpoints."""

    def __init__(self, width=960, height=320, line_width=2):
        """Initialize member variables."""
        super().__init__()
        self.line_width = line_width
        self._init_errors_plot(width, height)
        self.summary_n = widgets.markups.Paragraph(width=100)
        self.summary_mean = widgets.markups.Paragraph(width=100)
        self.summary_stdev = widgets.markups.Paragraph(width=100)
        self.summary_rmse = widgets.markups.Paragraph(width=100)
        self.column_layout = layouts.column([
            self.errors_fig,
            layouts.row([
                self.summary_n, self.summary_mean,
                self.summary_stdev, self.summary_rmse
            ])
        ])

    def _init_errors_plot(self, plot_width, plot_height):
        """Initialize member variables for error plotting."""
        self.errors = []
        self.errors_fig = figure(
            title='Converged Position Errors',
            plot_width=plot_width, plot_height=plot_height
        )
        self.errors_fig.xaxis.axis_label = 'Error from Target Position'
        self.errors_fig.yaxis.axis_label = 'Relative Frequency'
        self.errors_hist = None

    def add_error(self, target_position, converged_position):
        """Add an error measurement to the histogram."""
        self.errors.append(target_position - converged_position)
        (self.hist, self.edges) = np.histogram(self.errors, density=True, bins='auto')
        if self.errors_hist is not None:
            self.errors_fig.renderers.remove(self.errors_hist)
        self._update_summary()
        self.errors_hist = self.errors_fig.quad(
            top=self.hist, bottom=0, left=self.edges[:-1], right=self.edges[1:],
            line_width=self.line_width
        )

    def _update_summary(self):
        """Update data summary display."""
        self.summary_n.text = '{} samples'.format(len(self.errors))
        self.summary_mean.text = 'Mean: {:.2f}'.format(np.mean(self.errors))
        self.summary_stdev.text = 'Stdev: {:.2f}'.format(np.std(self.errors))
        self.summary_rmse.text = 'RMSE: {:.2f}'\
            .format(np.sqrt(np.mean(np.square(self.errors))))

    def clear(self):
        """Remove all data from the histogram plot."""
        if self.errors_hist is not None:
            self.errors_fig.renderers.remove(self.errors_hist)
            self.errors_hist = None
            self.summary_n.text = ''
            self.summary_mean.text = ''
            self.summary_stdev.text = ''
            self.summary_rmse.text = ''
        self.errors = []

    # Implement DocumentLayout

    @property
    def layout(self):
        """Return a document layout element."""
        return self.column_layout


class ErrorsPlotter(DocumentModel):
    """Plot of errors in final converged position, synchronized across documents."""

    def __init__(self, *args, **kwargs):
        """Initialize member variables."""
        super().__init__(ErrorsPlot, *args, **kwargs)

    def add_error(self, target_position, converged_position):
        """Add an error measurement to the histogram."""
        self.update_docs(lambda plot: plot.add_error(
            target_position, converged_position
        ))

    def clear(self):
        """Remove all data from the histogram."""
        self.update_docs(lambda plot: plot.clear())
