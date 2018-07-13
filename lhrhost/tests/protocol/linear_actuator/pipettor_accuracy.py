"""Test LinearActuator RPC command functionality."""
# Standard imports
import asyncio
import logging

# Local package imports
from lhrhost.messaging.presentation import BasicTranslator
from lhrhost.messaging.transport.actors import ResponseReceiver, TransportManager
from lhrhost.protocol.linear_actuator import Printer, Protocol
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
        self.p_printer = Printer('P-Axis', prefix=batch.RESPONSE_PREFIX)
        self.p = Protocol('PAxis', 'p', response_receivers=[self.p_printer])
        self.z = Protocol('ZAxis', 'z')
        self.y = Protocol('YAxis', 'y')
        # self.response_printer = MessagePrinter(prefix=batch.RESPONSE_PREFIX)
        self.translator = BasicTranslator(
            # message_receivers=[self.response_printer, self.z, self.y, self.p]
            message_receivers=[self.z, self.y, self.p]
        )
        self.p.command_receivers.append(self.translator)
        self.z.command_receivers.append(self.translator)
        self.y.command_receivers.append(self.translator)
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
        fluid_amount = 20

        print('Running test routine...')
        await asyncio.gather(
            self.p.initialized.wait(),
            self.z.initialized.wait(),
            self.y.initialized.wait()
        )
        await self.p.motor.request_complete(255)

        print('Moving to cuvette...')
        await self.y.feedback_controller.request_complete(30)
        print('  Y-Axis now at {}'.format(self.y.position.last_response_payload))

        while True:
            fluid_amount = await self.prompt.number(
                'Move sample platform to cuvette row. Amount to intake/dispense?',
                fluid_amount
            )
            print('Preparing pipettor for intake...')
            await self.p.feedback_controller.pid.kd.request(int(0.4 * 100))
            await self.p.feedback_controller.request_complete(int(650 + fluid_amount / 2))
            await asyncio.sleep(0.5)
            print('Performing intake...')
            await self.z.feedback_controller.request_complete(400)
            await asyncio.sleep(0.5)
            await self.intake(fluid_amount)
            await asyncio.sleep(0.5)
            await self.p.position.request()
            print('  Pre-dispense position: {}'.format(
                self.p.position.last_response_payload
            ))
            await asyncio.sleep(0.5)
            await self.z.feedback_controller.request_complete(970)
            await self.prompt('Move sample platform to the weigh boat...')
            await self.z.feedback_controller.request_complete(200)
            await asyncio.sleep(0.5)
            await self.p.motor.request_complete(255)
            await asyncio.sleep(0.5)
            await self.z.feedback_controller.request_complete(970)

        print(batch.OUTPUT_FOOTER)
        print('Quitting...')

    async def intake(self, fluid_amount):
        """Intake a fluid amount specified by position delta."""
        derivative_gains = {
            100: 0.4,
            50: 0.5,
            40: 0.9,
            30: 0.9,
            20: 1
        }
        k_d = derivative_gains[fluid_amount]
        await self.p.feedback_controller.pid.kd.request(int(k_d * 100))
        await self.p.position.request()
        print('  Pre-intake position: {}'.format(
            self.p.position.last_response_payload
        ))
        await self.p.feedback_controller.request_complete(
            self.p.position.last_response_payload - fluid_amount
        )


if __name__ == '__main__':
    main(Batch)
