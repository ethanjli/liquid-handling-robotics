"""Calibrate a linear actuator's sensor positions to physical positions."""

# Standard imports
import asyncio
import logging
import random

# Local package imports
from lhrhost.messaging.presentation import BasicTranslator
from lhrhost.messaging.transport.actors import ResponseReceiver, TransportManager
from lhrhost.robot.p_axis import Axis
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
        self.axis.load_pid_json()
        print('Physical calibration:', self.axis.calibration_data['parameters'])

        print('Testing physical position targeting...')
        positions = list(range(0, 910, 50))
        random.shuffle(positions)
        for position in positions:
            print('Moving to the {} mL mark...'.format(position / 1000))
            try:
                await self.axis.go_to_physical_position(position / 1000)
            except Exception as e:
                print(e)
            await asyncio.sleep(0.5)
            converged_position = await self.axis.physical_position
            print('Converged at the {:.3f} mL mark!'.format(converged_position))
            await self.prompt('Press enter to continue: ')

        print('Testing physical position displacements...')
        await self.axis.go_to_low_end_position()
        await asyncio.sleep(0.5)
        for i in range(0, 18):
            print('Moving up by a 0.05 mL marking...')
            actual_displacement = await self.axis.move_by_physical_delta(0.05)
            print('Moved up by {:.3f} mL markings!'.format(actual_displacement))
            await self.prompt('Press enter to continue: ')

        print('Testing precise volume intake/dispense...')
        await self.axis.go_to_low_end_position()
        await asyncio.sleep(0.5)
        for volume in [0.02, 0.03, 0.04, 0.05, 0.1]:
            print('Preparing for intake...')
            await self.axis.move_pre_intake(volume)
            await asyncio.sleep(1.0)
            print('Executing intake of {} mL...'.format(volume))
            actual_intake = await self.axis.intake(volume)
            print('Completed intake of {:.3f} mL!'.format(actual_intake))
            await asyncio.sleep(1.0)
            print('Executing dispense...')
            await self.axis.dispense()
            await self.prompt('Press enter to continue: ')

        print(batch.OUTPUT_FOOTER)
        print('Quitting...')


if __name__ == '__main__':
    main(Batch)
