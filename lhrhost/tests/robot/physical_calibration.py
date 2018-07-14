"""Calibrate a linear actuator's sensor positions to physical positions."""

# Standard imports
import asyncio
import logging
import random

# Local package imports
from lhrhost.messaging.presentation import BasicTranslator
from lhrhost.messaging.transport.actors import ResponseReceiver, TransportManager
from lhrhost.tests.dashboard.pid_tuning import main
from lhrhost.tests.messaging.transport.batch import (
    Batch, BatchExecutionManager, LOGGING_CONFIG
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

    def __init__(self, transport_loop, axis):
        """Initialize member variables."""
        self.arbiter = arbiter(start=self._start, stopping=self._stop)
        if axis == 'p':
            from lhrhost.robot.p_axis import Axis
        elif axis == 'z':
            from lhrhost.robot.z_axis import Axis
        elif axis == 'y':
            from lhrhost.robot.y_axis import Axis
        else:
            raise NotImplementedError('Axis {} is not supported!'.format(axis))
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

        calibration_samples = []

        try:
            while True:
                sensor_position = await self.prompt.number(
                    'Move to sensor position:',
                    random.randint(*self.axis.last_position_limits)
                )
                await self.axis.go_to_sensor_position(sensor_position)
                await asyncio.sleep(0.5)
                sensor_position = await self.axis.position
                print('Moved to sensor position {}.'.format(sensor_position))
                physical_position = await self.prompt.number(
                    'What is the corresponding physical position? (None to finish)',
                    None, float
                )
                if physical_position is None:
                    break
                calibration_samples.append((sensor_position, physical_position))
        except KeyboardInterrupt:
            pass

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


if __name__ == '__main__':
    main(Batch)
