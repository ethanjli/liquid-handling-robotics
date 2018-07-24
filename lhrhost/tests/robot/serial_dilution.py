"""Test the robot abstraction layer with a serial dilution demo."""

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

        dilution_rows = ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a']
        await self.dispense_waste()
        await self.intake_water('mid', 0.85)
        await self.distribute_water(0.1, [1], dilution_rows)
        await self.dispense_waste()
        await self.intake_food_coloring(0.1)
        for row in dilution_rows:
            await self.dilute(1, row, 'low', 0.1, 2)
        await self.dispense_waste()
        await self.robot.z.go_to_high_end_position()
        await self.robot.y.go_to_low_end_position()

        print(batch.OUTPUT_FOOTER)
        print('Quitting...')

    async def intake_water(self, height, volume):
        """Intake water to distribute to wells."""
        await self.robot.go_to_cuvette('g')
        await self.robot.dispense('cuvette', height)
        await self.robot.intake('cuvette', height, volume)

    async def intake_food_coloring(self, volume):
        """Intake food coloring to distribute to wells."""
        await self.robot.go_to_cuvette('f')
        await self.robot.intake('cuvette', 'bottom', volume)

    async def distribute_water(self, volume, columns, rows):
        """Distribute water to wells."""
        for column in columns:
            for row in rows:
                await self.robot.go_to_96_well_plate(column, row)
                await self.robot.dispense('96-well plate', 'mid', volume)

    async def dilute(self, column, row, height, volume, mix_cycles):
        """Dilute food coloring in a well."""
        await self.robot.go_to_96_well_plate(column, row)
        for i in range(mix_cycles):
            await self.robot.dispense('96-well plate', height, None)
            await self.robot.intake('96-well plate', height, volume)

    async def dispense_waste(self):
        """Dispense any leftover liquid in the pipettor."""
        await self.robot.go_to_cuvette('a')
        await self.robot.dispense('cuvette', 'top')


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
