"""Test LinearActuator state plotting functionality."""
# Standard imports
import argparse
import asyncio
import logging

# Local package imports
from lhrhost.dashboard.linear_actuator.plots import LinearActuatorPlotter as Plotter
from lhrhost.messaging import (
    MessagingStack,
    add_argparser_transport_selector, parse_argparser_transport_selector
)
from lhrhost.protocol.linear_actuator import Protocol
from lhrhost.tests.messaging.transport.batch import (
    BatchExecutionManager, LOGGING_CONFIG
)
from lhrhost.util import batch

# Logging
logging.config.dictConfig(LOGGING_CONFIG)


class Batch:
    """Actor-based batch execution."""

    def __init__(self, transport_loop, axis):
        """Initialize member variables."""
        self.messaging_stack = MessagingStack(transport_loop)
        self.protocol = Protocol('{}-Axis'.format(axis.upper()), axis)
        self.protocol_plotter = Plotter(self.protocol)
        self.messaging_stack.register_response_receivers(self.protocol)
        self.messaging_stack.register_command_senders(self.protocol)
        self.batch_execution_manager = BatchExecutionManager(
            self.messaging_stack.arbiter, self.messaging_stack.command_sender,
            self.test_routine, header=batch.OUTPUT_HEADER,
            ready_waiter=self.messaging_stack.connection_synchronizer.wait_connected
        )
        self.messaging_stack.register_execution_manager(self.batch_execution_manager)
        print('Showing plot...')
        self.protocol_plotter.show()

    async def test_routine(self):
        """Run the batch execution test routine."""
        print('Running test routine...')
        await self.protocol.initialized.wait()
        self.colors = {
            0: 'gray',  # braking
            -1: 'orange',  # stalled
            -2: 'green',  # converged
            -3: 'red',  # timer
        }

        print('Motor position feedback control with position and motor duty notification')
        await self.protocol.position.notify.change_only.request(0)
        await self.protocol.position.notify.interval.request(20)
        await self.protocol.motor.notify.change_only.request(0)
        await self.protocol.motor.notify.interval.request(20)
        await self.protocol.position.notify.request(2)
        await self.protocol.motor.notify.request(2)
        for i in range(10):
            await self.go_to_position(100)
            await asyncio.sleep(0.5)
            await self.go_to_position(700)
            await asyncio.sleep(0.5)
        await self.protocol.position.notify.request(0)
        await self.protocol.motor.notify.request(0)

        print(batch.OUTPUT_FOOTER)
        print('Idling...')
        self.protocol_plotter.server.run_until_shutdown()

    async def go_to_position(self, position):
        """Send the actuator to the specified position."""
        self.protocol_plotter.position_plotter.add_arrow(position, slope=2)
        self.protocol_plotter.duty_plotter.start_state_region()
        await self.protocol.feedback_controller.request_complete(position)
        self.protocol_plotter.duty_plotter.add_state_region(
            self.colors[self.protocol.last_response_payload]
        )


def main():
    """Test batch scripted control of a linear actuator."""
    parser = argparse.ArgumentParser(
        description='Test batch scripted control of a linear actuator.'
    )
    add_argparser_transport_selector(parser)
    parser.add_argument(
        'axis', choices=['p', 'z', 'y', 'x'],
        help='Linear actuator axis.'
    )
    args = parser.parse_args()
    transport_loop = parse_argparser_transport_selector(args)
    batch = Batch(transport_loop, args.axis)
    batch.messaging_stack.run()


if __name__ == '__main__':
    main()
