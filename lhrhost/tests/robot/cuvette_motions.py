"""Test the robot abstraction layer with repeated cuvette column motions."""

# Standard imports
import argparse
import logging

# Local package imports
from lhrhost.messaging import (
    MessagingStack,
    add_argparser_transport_selector, parse_argparser_transport_selector
)
from lhrhost.robot import Robot
from lhrhost.tests.messaging.transport.batch import (
    BatchExecutionManager, LOGGING_CONFIG
)
from lhrhost.util import batch

# Logging
# LOGGING_CONFIG['loggers']['lhrhost'] = {'level': 'DEBUG'}
logging.config.dictConfig(LOGGING_CONFIG)


class Batch:
    """Actor-based batch execution."""

    def __init__(self, transport_loop):
        """Initialize member variables."""
        self.messaging_stack = MessagingStack(transport_loop)
        self.robot = Robot()
        self.robot.register_messaging_stack(self.messaging_stack)
        self.batch_execution_manager = BatchExecutionManager(
            self.messaging_stack.arbiter, self.messaging_stack.command_sender,
            self.test_routine, header=batch.OUTPUT_HEADER,
            ready_waiter=self.messaging_stack.connection_synchronizer.wait_connected
        )
        self.messaging_stack.register_execution_manager(self.batch_execution_manager)

    async def test_routine(self):
        """Run the batch execution test routine."""
        print('Running test routine...')
        print('Waiting for axes to initialize...')
        await self.robot.wait_until_initialized()
        print('Synchronizing robot state with peripheral...')
        await self.robot.synchronize_values()
        print('Loading calibration data...')
        await self.robot.load_calibrations()
        await self.robot.go_to_alignment_hole()

        print('Starting cuvette test...')
        await self.robot.go_to_cuvette('a')
        await self.robot.dispense('cuvette', 'far above')
        for height in ['bottom', 'low', 'mid', 'high', 'top', 'above', 'far above']:
            print('Testing with height {}...'.format(height))
            # for (row, volume) in [('a', 20), ('b', 30), ('c', 40), ('d', 50), ('e', 100)]:
            #     print(
            #         '  Testing precise with row {} and volume {} mL...'
            #         .format(row, volume)
            #     )
            #     await self.test_individual_precise(row, height, volume / 1000)
            # for (row, volume) in [
            #     ('f', 100), ('g', 200), ('a', 300), ('b', 400),
            #     ('c', 500), ('d', 600), ('e', 700), ('f', 800), ('g', 900)
            # ]:
            #     print(
            #         '  Testing rough with row {} and volume {} mL...'
            #         .format(row, volume / 1000)
            #     )
            #     await self.test_individual_rough(row, height, volume / 1000)
            for (row, volume) in [
                ('g', 50), ('a', 100), ('b', 150), ('c', 200),
                ('d', 250), ('e', 300), ('f', 350), ('g', 400)
            ]:
                num_folds = 900 // volume
                print(
                    '  Testing {}-fold repeating with row {} and volume {} mL...'
                    .format(num_folds, row, volume / 1000)
                )
                try:
                    await self.test_individual_repeater(row, height, volume / 1000, num_folds)
                except Exception as e:
                    print(e)
        await self.robot.z.go_to_high_end_position()
        await self.robot.y.go_to_low_end_position()

        print(batch.OUTPUT_FOOTER)
        print('Quitting...')

    async def test_individual_precise(self, cuvette_row, height, volume):
        """Intake precise volumes of water from a cuvette."""
        await self.robot.go_to_cuvette(cuvette_row)
        await self.robot.intake_precise('cuvette', height, volume)
        await self.robot.dispense('cuvette', height)

    async def test_individual_rough(self, cuvette_row, height, volume):
        """Intake rough volumes of water from a cuvette."""
        await self.robot.go_to_cuvette(cuvette_row)
        await self.robot.intake('cuvette', height, volume)
        await self.robot.dispense('cuvette', height, volume)

    async def test_individual_repeater(self, cuvette_row, height, volume, folds):
        """Intake repeater volumes of water from a cuvette."""
        await self.robot.go_to_cuvette(cuvette_row)
        await self.robot.intake('cuvette', height, volume * folds)
        for i in range(folds):
            await self.robot.dispense('cuvette', height, volume)
        await self.robot.dispense('cuvette', height)


def main():
    """Run a serial dilution demo."""
    parser = argparse.ArgumentParser(
        description='Run a serial dilution demo.'
    )
    add_argparser_transport_selector(parser)
    args = parser.parse_args()
    transport_loop = parse_argparser_transport_selector(args)
    batch = Batch(transport_loop)
    batch.messaging_stack.run()


if __name__ == '__main__':
    main()
