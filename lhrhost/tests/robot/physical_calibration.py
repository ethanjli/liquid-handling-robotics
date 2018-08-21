"""Calibrate a linear actuator's sensor positions to physical positions."""

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

    def __init__(self, transport_loop, axis):
        """Initialize member variables."""
        self.messaging_stack = MessagingStack(transport_loop)
        if axis == 'p':
            from lhrhost.robot.p_axis import Axis
        elif axis == 'z':
            from lhrhost.robot.z_axis import Axis
        elif axis == 'y':
            from lhrhost.robot.y_axis import Axis
        else:
            from lhrhost.robot.x_axis import Axis
        self.axis = Axis()
        if axis == 'p':
            self.axis.load_pid_json()
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

        print('Waiting for axis initialization...')
        await self.axis.wait_until_initialized()
        print('Synchronizing axis values...')
        await self.axis.synchronize_values()

        calibration_samples = []
        print('Collecting calibration samples...')
        while True:
            sensor_position = await self.prompt.number(
                'Move to sensor position:',
                random.randint(*self.axis.last_position_limits)
            )
            await self.axis.go_to_sensor_position(sensor_position)
            await asyncio.sleep(0.5)
            sensor_position = await self.axis.sensor_position
            print('Moved to sensor position {}.'.format(sensor_position))
            physical_position = await self.prompt.number(
                'What is the corresponding physical position? (None to finish)',
                None, float
            )
            if physical_position is None:
                break
            calibration_samples.append((sensor_position, physical_position))

        print(
            'Performing linear regression with {} samples...'
            .format(len(calibration_samples))
        )
        for calibration_sample in calibration_samples:
            self.axis.add_calibration_sample(*calibration_sample)
        linear_regression = self.axis.fit_calibration_linear()
        print(
            'Linreg slope: {:.4f}; intercept: {:.4f}; R-value: {:.4f}; stderr: {:.4f}'
            .format(*linear_regression)
        )

        output_path = await self.prompt.string(
            'Save calibration data to path:',
            'calibrations/{}_physical.json'.format(self.axis.name)
        )
        self.axis.save_calibration_json(output_path)

        print(batch.OUTPUT_FOOTER)
        print('Quitting...')


def main():
    """Calibrate an axis's sensor positions to physical positions."""
    parser = argparse.ArgumentParser(
        description='Calibrate an axis\'s sensor positions to physical positions.'
    )
    add_argparser_transport_selector(parser)
    parser.add_argument(
        'axis', choices=['p', 'z', 'y', 'x'],
        help='Linear actuator axis.'
    )
    args = parser.parse_args()
    transport_loop = parse_argparser_transport_selector(args)
    batch = Batch(transport_loop, args.axis)
    batch.messaging_stack.run()


if __name__ == '__main__':
    main()
