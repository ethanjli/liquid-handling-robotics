"""Test the z-axis abstraction layer."""

# Standard imports
import argparse
import logging

# Local package imports
from lhrhost.messaging import (
    MessagingStack,
    add_argparser_transport_selector, parse_argparser_transport_selector
)
from lhrhost.robot.z_axis import Axis
from lhrhost.tests.messaging.transport.batch import (
    BatchExecutionManager, LOGGING_CONFIG
)
from lhrhost.util import batch
from lhrhost.util.cli import Prompt

# Logging
# LOGGING_CONFIG['loggers']['lhrhost'] = {'level': 'DEBUG'}
logging.config.dictConfig(LOGGING_CONFIG)


class Batch():
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


def main():
    """Test the z-axis abstraction layer."""
    parser = argparse.ArgumentParser(
        description='Test the z-axis abstraction layer.'
    )
    add_argparser_transport_selector(parser)
    args = parser.parse_args()
    transport_loop = parse_argparser_transport_selector(args)
    batch = Batch(transport_loop)
    batch.messaging_stack.run()


if __name__ == '__main__':
    main()
