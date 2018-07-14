"""Calibrate a linear actuator's sensor positions to physical positions."""

# Standard imports
import asyncio
import logging
import random

# Local package imports
from lhrhost.messaging.presentation import BasicTranslator
from lhrhost.messaging.transport.actors import ResponseReceiver, TransportManager
from lhrhost.robot.y_axis import Axis
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

        print('Moving to alignment hole...')
        await self.axis.go_to_physical_position(0)
        await self.prompt('Press enter to continue: ')

        print('Testing physical position targeting...')
        positions = list(range(0, 100, 10))
        random.shuffle(positions)
        for position in positions:
            print('Moving to {} cm from the alignment hole...'.format(position / 10))
            try:
                await self.axis.go_to_physical_position(position / 10)
            except Exception as e:
                print(e)
            await asyncio.sleep(0.5)
            converged_position = await self.axis.physical_position
            print('Converged at {:.3f} cm!'.format(converged_position))
            await self.prompt('Press enter to continue: ')

        print('Testing physical position displacements...')
        await self.axis.go_to_end_position(speed=-255)
        await asyncio.sleep(0.5)
        for i in range(0, 10):
            print('Moving away from the alignment hole by 1 cm...')
            actual_displacement = await self.axis.move_by_physical_delta(1)
            print('Moved away {:.3f} cm!'.format(actual_displacement))
            await self.prompt('Press enter to continue: ')

        print('Testing discrete position targeting...')
        await self.axis.go_to_end_position(speed=-255)
        await self.prompt('Testing cuvette positioning: ')
        for cuvette_row in ['a', 'b', 'c', 'd', 'e', 'f', 'g']:
            await self.axis.move_cuvette(cuvette_row)
            await self.prompt('Press enter to continue: ')
        await self.prompt('Testing 96-well plate positioning: ')
        for plate_row in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
            await self.axis.move_96_well_plate(plate_row)
            await self.prompt('Press enter to continue: ')

        print(batch.OUTPUT_FOOTER)
        print('Quitting...')


if __name__ == '__main__':
    main(Batch)
