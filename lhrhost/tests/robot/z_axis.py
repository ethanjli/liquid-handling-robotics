"""Calibrate a linear actuator's sensor positions to physical positions."""

# Standard imports
import logging

# Local package imports
from lhrhost.messaging.presentation import BasicTranslator
from lhrhost.messaging.transport.actors import ResponseReceiver, TransportManager
from lhrhost.robot.z_axis import Axis
from lhrhost.tests.messaging.transport.batch import (
    Batch, BatchExecutionManager, LOGGING_CONFIG, main
)
from lhrhost.util import batch
from lhrhost.util.cli import Prompt

# External imports
from pulsar.api import arbiter

# Logging
# LOGGING_CONFIG['loggers']['lhrhost'] = {'level': 'DEBUG'}
logging.config.dictConfig(LOGGING_CONFIG)


class Batch(Batch):
    """Actor-based batch execution."""

    def __init__(self, transport_loop):
        """Initialize member variables."""
        self.arbiter = arbiter(start=self._start, stopping=self._stop)
        self.axis = Axis()
        self.translator = BasicTranslator(
            message_receivers=[self.axis.protocol]
        )
        self.axis.protocol.command_receivers.append(self.translator)
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

    async def test_routine(self):
        """Run the batch execution test routine."""
        self.prompt = Prompt(end='', flush=True)

        print('Running test routine...')
        await self.axis.wait_until_initialized()
        await self.axis.synchronize_values()
        self.axis.load_calibration_json()
        self.axis.load_discrete_json()
        print('Physical calibration:', self.axis.calibration_data['parameters'])

        print('Testing discrete position targeting...')
        relative_heights = ['above', 'top', 'high', 'mid', 'low', 'bottom']

        await self.axis.go_to_high_end_position()
        await self.prompt('Testing cuvette positioning: ')
        for height in relative_heights:
            print('Moving to {}...'.format(height))
            await self.axis.go_to_cuvette(height)
            await self.prompt('Press enter to continue: ')
            await self.axis.go_to_cuvette('far above')
        await self.axis.go_to_high_end_position()
        await self.prompt('Testing 96-well plate positioning: ')
        for height in relative_heights:
            print('Moving to {}...'.format(height))
            await self.axis.go_to_96_well_plate(height)
            await self.prompt('Press enter to continue: ')
            await self.axis.go_to_96_well_plate('far above')

        print(batch.OUTPUT_FOOTER)
        print('Quitting...')


if __name__ == '__main__':
    main(Batch)
