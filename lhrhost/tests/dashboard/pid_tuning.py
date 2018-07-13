"""Test LinearActuator state plotting functionality."""
# Standard imports
import argparse
import asyncio
import logging

# External imports
from bokeh import layouts
from bokeh.models import widgets

# Local package imports
from lhrhost.dashboard import DocumentLayout, DocumentModel
from lhrhost.dashboard.linear_actuator.feedback_controller import FeedbackControllerModel
from lhrhost.dashboard.linear_actuator.plots import LinearActuatorPlotter as Plotter
from lhrhost.messaging.presentation import BasicTranslator
from lhrhost.messaging.transport.actors import ResponseReceiver, TransportManager
from lhrhost.protocol.linear_actuator import Protocol
from lhrhost.tests.messaging.transport.batch import (
    Batch, BatchExecutionManager, LOGGING_CONFIG
)
from lhrhost.util.cli import Prompt

# External imports
from pulsar.api import arbiter

# Logging
logging.config.dictConfig(LOGGING_CONFIG)


class LinearActuatorControlPanel(DocumentLayout):
    """Linear actuator controller."""

    def __init__(self, plotter, feedback_controller, title):
        """Initialize member variables."""
        super().__init__()

        self.plotter = plotter.make_document_layout()
        self.feedback_controller = feedback_controller.make_document_layout()

        self.column_layout = layouts.column([
            layouts.widgetbox([widgets.Div(text='<h1>{}</h1>'.format(title))]),
            self.plotter.layout,
            self.feedback_controller.layout
        ])

    # Implement DocumentLayout

    @property
    def layout(self):
        """Return a document layout element."""
        return self.column_layout

    def initialize_doc(self, doc, as_root=False):
        """Initialize the provided document."""
        super().initialize_doc(doc, as_root)
        self.plotter.initialize_doc(self.document)
        self.feedback_controller.initialize_doc(self.document)


class LinearActuatorControlModel(DocumentModel):
    """Linear actuator controller, synchronized across documents."""

    def __init__(self, linear_actuator_protocol, *args, **kwargs):
        """Initialize member variables."""
        self.plotter = Plotter(
            linear_actuator_protocol, width=900, height=240, nest_level=1, title=''
        )
        self.feedback_controller = FeedbackControllerModel(
            linear_actuator_protocol, nest_level=1, width=900, title=''
        )
        super().__init__(
            LinearActuatorControlPanel, self.plotter, self.feedback_controller,
            linear_actuator_protocol.channel_path
        )


class Batch(Batch):
    """Actor-based batch execution."""

    def __init__(self, transport_loop, axis):
        """Initialize member variables."""
        self.arbiter = arbiter(start=self._start, stopping=self._stop)
        self.protocol = Protocol('{}-Axis'.format(axis.upper()), axis)
        self.dashboard = LinearActuatorControlModel(self.protocol)
        self.translator = BasicTranslator(
            message_receivers=[self.protocol]
        )
        self.protocol.command_receivers.append(self.translator)
        self.response_receiver = ResponseReceiver(
            response_receivers=[self.translator]
        )
        self.transport_manager = TransportManager(
            self.arbiter, transport_loop, response_receiver=self.response_receiver
        )
        self.translator.serialized_message_receivers.append(
            self.transport_manager.command_sender
        )
        self.batch_execution_manager = BatchExecutionManager(
            self.arbiter, self.transport_manager.command_sender, self.test_routine,
            ready_waiter=self.transport_manager.connection_synchronizer.wait_connected
        )
        print('Showing dashboard...')
        self.dashboard.show()

    async def test_routine(self):
        """Run the batch execution test routine."""
        self.prompt = Prompt(end='', flush=True)

        print('Waiting for {} to initialize...'.format(self.protocol.channel_path))
        await self.protocol.initialized.wait()
        self.colors = {
            0: 'gray',  # braking
            -1: 'orange',  # stalled
            -2: 'green',  # converged
            -3: 'red',  # timer
        }

        print('Requesting all motor parameter values...')
        await self.protocol.motor.request_all()

        print('Requesting all feedback controller parameter values...')
        await self.protocol.feedback_controller.request_all()

        self.num_cycles = 5
        self.low_position = 100
        self.high_position = 700
        await self.set_test_parameters()
        await self.prompt('Press enter to begin: ')
        await self.dashboard.plotter.toggler.start_plotting()
        try:
            while True:
                for i in range(self.num_cycles):
                    await self.go_to_position(self.low_position)
                    await asyncio.sleep(0.5)
                    await self.go_to_position(self.high_position)
                    await asyncio.sleep(0.5)
                print('Finished test cycles!')
                self.dashboard.plotter.position_plotter.stop_plotting()
                self.dashboard.plotter.duty_plotter.stop_plotting()
                await self.set_test_parameters()
                await self.prompt('Press enter to restart: ')
                self.dashboard.plotter.position_plotter.clear()
                self.dashboard.plotter.duty_plotter.clear()
                if self.dashboard.plotter.toggler.plotting:
                    self.dashboard.plotter.position_plotter.start_plotting()
                    self.dashboard.plotter.duty_plotter.start_plotting()
        except KeyboardInterrupt:
            await self.dashboard.plotter.toggler.stop_plotting()

        print('Idling...')
        self.dashboard.plotter.server.run_until_shutdown()

    async def set_test_parameters(self):
        """Set the test motion parameters."""
        self.num_cycles = await self.prompt.number(
            'How many test cycles to run?', self.num_cycles
        )
        self.low_position = await self.prompt.number(
            'Low target position?', self.low_position
        )
        self.high_position = await self.prompt.number(
            'High target position?', self.high_position
        )

    async def go_to_position(self, position):
        """Send the actuator to the specified position."""
        self.dashboard.plotter.position_plotter.add_arrow(position, slope=2)
        self.dashboard.plotter.duty_plotter.start_state_region()
        await self.protocol.feedback_controller.request_complete(position)
        self.dashboard.plotter.duty_plotter.add_state_region(
            self.colors[self.protocol.last_response_payload]
        )
        self.dashboard.feedback_controller.errors_plotter.add_error(
            position, self.protocol.position.last_response_payload
        )


def main(console_class):
    """Run a dashboard using the selected transport-layer implementation and actuator."""
    parser = argparse.ArgumentParser(
        description='Perform PID tuning for the selected transport and actuator axis.'
    )
    parser.add_argument(
        'transport', choices=['ascii', 'firmata'],
        help='Transport-layer implementation.'
    )
    parser.add_argument(
        'axis', choices=['p', 'z', 'y', 'x'],
        help='Linear actuator axis.'
    )
    args = parser.parse_args()
    if args.transport == 'ascii':
        from lhrhost.messaging.transport.ascii import transport_loop
    elif args.transport == 'firmata':
        from lhrhost.messaging.transport.firmata import transport_loop
    else:
        raise NotImplementedError(
            'Unknown transport layer implementation: {}'.format(transport_loop)
        )
    console = console_class(transport_loop, args.axis)
    console.run()


if __name__ == '__main__':
    main(Batch)