"""Test LinearActuator webcam imaging functionality."""
# Standard imports
import asyncio
import logging

# Local package imports
from lhrhost.imaging.plotter import ImagePlotter as Plotter
from lhrhost.imaging.webcam import Camera
from lhrhost.messaging.presentation import BasicTranslator
from lhrhost.messaging.transport.actors import ResponseReceiver, TransportManager
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

        self.image_plotter = Plotter()
        self.camera = Camera(image_receivers=[self.image_plotter])

        self.protocol = Protocol('Y-Axis', 'y')
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
        print('Showing webcam display...')
        self.image_plotter.show()

    async def test_routine(self):
        """Run the batch execution test routine."""
        print('Starting webcam...')
        self.camera.open(1)
        print('Running test routine...')
        await self.protocol.initialized.wait()

        print('Moving actuator around...')
        for i in range(5):
            await self.protocol.feedback_controller.request_complete(0)
            await self.camera.capture_image()
            await asyncio.sleep(1.0)
            await self.protocol.feedback_controller.request_complete(720)
            await self.camera.capture_image()
            await asyncio.sleep(1.0)

        print(batch.OUTPUT_FOOTER)
        print('Stopping webcam...')
        self.camera.close()
        print('Quitting...')


if __name__ == '__main__':
    main(Batch)
