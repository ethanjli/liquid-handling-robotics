"""Calibrate a linear actuator's sensor positions to physical positions."""

# Standard imports
import logging

# Local package imports
from lhrhost.messaging.presentation import BasicTranslator
from lhrhost.messaging.transport.actors import ResponseReceiver, TransportManager
from lhrhost.robot import Robot
from lhrhost.tests.messaging.transport.batch import (
    Batch, BatchExecutionManager, LOGGING_CONFIG, main
)
from lhrhost.util import batch

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
        self.robot = Robot()
        self.translator = BasicTranslator(
            message_receivers=[
                self.robot.p.protocol, self.robot.z.protocol, self.robot.y.protocol
            ]
        )
        self.robot.p.protocol.command_receivers.append(self.translator)
        self.robot.z.protocol.command_receivers.append(self.translator)
        self.robot.y.protocol.command_receivers.append(self.translator)
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
        print('Running test routine...')
        try:
            print('Waiting for axes to initialize...')
            await self.robot.wait_until_initialized()
            print('Synchronizing robot state with peripheral...')
            await self.robot.synchronize_values()
            print('Loading calibration data...')
            await self.robot.load_calibrations()
            await self.robot.go_to_alignment_hole()

            await self.dispense_waste()
            await self.intake_water('mid', 0.85)
            await self.distribute_water(0.2, [1], ['h', 'g', 'f', 'e'])
            await self.dispense_waste()
            await self.intake_water('mid', 0.85)
            await self.distribute_water(0.2, [1], ['d', 'c', 'b', 'a'])
            await self.dispense_waste()
            await self.intake_food_coloring(0.2)
            for row in ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a']:
                await self.dilute(1, row, 'low', 0.2, 2)
            await self.dispense_waste()
            await self.robot.z.go_to_high_end_position()
            await self.robot.y.go_to_low_end_position()
        except Exception as e:
            print(e)

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
        await self.robot.intake('cuvette', 'high', volume)

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
        await self.robot.go_to_cuvette('e')
        await self.robot.dispense('cuvette', 'top')


if __name__ == '__main__':
    main(Batch)
