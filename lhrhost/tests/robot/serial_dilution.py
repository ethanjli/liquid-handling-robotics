"""Test the robot abstraction layer with a serial dilution demo."""

# Standard imports
import argparse
import asyncio
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
        await self.robot.ensure_sample_platform_configuration('standard 96-well plate')
        print('Waiting for axes to initialize...')
        await self.robot.wait_until_initialized()
        print('Synchronizing robot state with peripheral...')
        await self.robot.synchronize_values()
        print('Loading calibration data...')
        await self.robot.load_calibrations()
        await self.robot.align_manually()

        dilution_columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        await self.dispense_waste()
        await self.intake_water('mid', 0.85)
        await self.distribute_water(dilution_columns, [1], 0.1)
        await self.dispense_waste()
        await self.intake_food_coloring(0.1)
        for column in dilution_columns:
            await self.dilute(column, 1, 'low', 0.1, 2)
        await self.dispense_waste()
        await self.robot.z.go_to_high_end_position()
        await asyncio.gather(
            self.robot.y.go_to_low_end_position(),
            self.robot.x.go_to_low_end_position()
        )

        print(batch.OUTPUT_FOOTER)
        print('Quitting...')

    async def intake_water(self, height, volume):
        """Intake water to distribute to wells."""
        await self.robot.go_to_module_position('cuvettes', 'a', 1)
        await self.robot.intake('cuvettes', volume=volume, height=height)

    async def intake_food_coloring(self, volume):
        """Intake food coloring to distribute to wells."""
        await self.robot.go_to_module_position('cuvettes', 'a', 2)
        await self.robot.intake('cuvettes', volume=volume, height='bottom')

    async def distribute_water(self, columns, rows, volume):
        """Distribute water to wells."""
        for column in columns:
            for row in rows:
                await self.robot.go_to_module_position('plate', column, row)
                await self.robot.dispense('plate', volume=volume, height='mid')

    async def dilute(self, column, row, height, volume, mix_cycles):
        """Dilute food coloring in a well."""
        await self.robot.go_to_module_position('plate', column, row)
        for i in range(mix_cycles):
            await self.robot.dispense('plate', height=height)
            await self.robot.intake('plate', volume=volume, height=height)

    async def dispense_waste(self):
        """Dispense any leftover liquid in the pipettor."""
        await self.robot.go_to_module_position('cuvettes', 'a', 3)
        await self.robot.dispense('cuvettes', height='top')


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
