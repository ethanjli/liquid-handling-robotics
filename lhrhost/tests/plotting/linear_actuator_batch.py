"""Test LinearActuator state plotting functionality."""
# Standard imports
import asyncio
import logging

# Local package imports
from lhrhost.messaging.presentation import BasicTranslator
from lhrhost.messaging.transport.actors import ResponseReceiver, TransportManager
from lhrhost.plotting.linear_actuator import LinearActuatorPlotter as Plotter
from lhrhost.protocol.linear_actuator import Protocol
from lhrhost.tests.messaging.transport.batch import (
    Batch, BatchExecutionManager, LOGGING_CONFIG, main
)
from lhrhost.util import batch

# External imports
from pulsar.api import arbiter

# Logging
logging.config.dictConfig(LOGGING_CONFIG)


class Batch(Batch):
    """Actor-based batch execution."""

    def __init__(self, transport_loop):
        """Initialize member variables."""
        self.arbiter = arbiter(start=self._start, stopping=self._stop)
        self.protocol_plotter = Plotter('Y-Axis State')
        self.protocol = Protocol(
            'Y-Axis', 'y',
            response_receivers=[self.protocol_plotter]
        )
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
            header=batch.OUTPUT_HEADER,
            ready_waiter=self.transport_manager.connection_synchronizer.wait_connected
        )
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
            await self.go_to_position(0)
            await asyncio.sleep(0.5)
            await self.go_to_position(720)
            await asyncio.sleep(0.5)
        await self.protocol.position.notify.request(0)
        await self.protocol.motor.notify.request(0)

        print(batch.OUTPUT_FOOTER)
        print('Quitting...')

    async def go_to_position(self, position):
        """Send the actuator to the specified position."""
        self.protocol_plotter.add_position_arrow(position)
        motion_start_time = self.protocol_plotter.last_duty_time
        await self.protocol.feedback_controller.request_complete(position)
        motion_end_time = self.protocol_plotter.last_duty_time
        self.protocol_plotter.add_duty_region(
            motion_start_time, motion_end_time,
            self.colors[self.protocol.last_response_payload]
        )


if __name__ == '__main__':
    main(Batch)
