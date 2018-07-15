"""Test the p-axis abstraction layer."""

# Standard imports
import argparse
import asyncio
import logging
import random

# Local package imports
from lhrhost.messaging import (
    MessagingStack,
    add_argparser_transport_selector, parse_argparser_transport_selector
)
from lhrhost.robot.p_axis import Axis
from lhrhost.tests.messaging.transport.batch import (
    BatchExecutionManager, LOGGING_CONFIG
)
from lhrhost.util import batch
from lhrhost.util.cli import Prompt

# Logging
# LOGGING_CONFIG['loggers']['lhrhost'] = {'level': 'DEBUG'}
logging.config.dictConfig(LOGGING_CONFIG)


class Batch:
    """Actor-based batch execution."""

    def __init__(self, transport_loop):
        """Initialize member variables."""
        self.messaging_stack = MessagingStack(transport_loop)
        self.axis = Axis()
        self.messaging_stack.register_response_receivers(self.axis.protocol)
        self.messaging_stack.register_command_senders(self.axis.protocol)
        self.batch_execution_manager = BatchExecutionManager(
            self.messaging_stack.arbiter, self.messaging_stack.command_sender,
            self.test_routine, header=batch.OUTPUT_HEADER,
            ready_waiter=self.messaging_stack.connection_synchronizer.wait_connected
        )
        self.messaging_stack.register_execution_manager(self.batch_execution_manager)

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
            await self.axis.go_to_pre_intake(volume)
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


def main():
    """Test the p-axis abstraction layer."""
    parser = argparse.ArgumentParser(
        description='Test the p-axis abstraction layer.'
    )
    add_argparser_transport_selector(parser)
    args = parser.parse_args()
    transport_loop = parse_argparser_transport_selector(args)
    batch = Batch(transport_loop)
    batch.messaging_stack.run()


if __name__ == '__main__':
    main()
