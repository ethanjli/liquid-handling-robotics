"""Test LinearActuator RPC command functionality."""
# Standard imports
import argparse
import asyncio
import logging

# Local package imports
from lhrhost.messaging import (
    MessagingStack,
    add_argparser_transport_selector, parse_argparser_transport_selector
)
from lhrhost.protocol.linear_actuator import Printer, Protocol
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
        self.p_printer = Printer('P-Axis', prefix=batch.RESPONSE_PREFIX)
        self.p = Protocol('PAxis', 'p', response_receivers=[self.p_printer])
        self.z = Protocol('ZAxis', 'z')
        self.y = Protocol('YAxis', 'y')
        self.messaging_stack.register_response_receivers(self.p)
        self.messaging_stack.register_response_receivers(self.z)
        self.messaging_stack.register_response_receivers(self.y)
        self.messaging_stack.register_command_senders(self.p)
        self.messaging_stack.register_command_senders(self.z)
        self.messaging_stack.register_command_senders(self.y)
        self.batch_execution_manager = BatchExecutionManager(
            self.messaging_stack.arbiter, self.messaging_stack.command_sender,
            self.test_routine, header=batch.OUTPUT_HEADER,
            ready_waiter=self.messaging_stack.connection_synchronizer.wait_connected
        )
        self.messaging_stack.register_execution_manager(self.batch_execution_manager)

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
        await self.p.motor.request_complete(-255)

        print('Moving to cuvette...')
        await self.y.feedback_controller.request_complete(720 - 30)
        print('  Y-Axis now at {}'.format(self.y.position.last_response_payload))

        while True:
            fluid_amount = await self.prompt.number(
                'Move sample platform to cuvette row. Amount to intake/dispense?',
                fluid_amount
            )
            print('Preparing pipettor for intake...')
            await self.p.feedback_controller.pid.kd.request(int(0.4 * 100))
            await self.p.feedback_controller.request_complete(1023 - int(650 + fluid_amount / 2))
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
            await self.p.motor.request_complete(-255)
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
            (self.p.position.last_response_payload + fluid_amount)
        )


def main():
    """Run the axes to test the linear actuator protocol for pipettor accuracy."""
    parser = argparse.ArgumentParser(
        description=(
            'Run the axes to test the linear actuator protocol for '
            'pipettor accuracy.'
        )
    )
    add_argparser_transport_selector(parser)
    args = parser.parse_args()
    transport_loop = parse_argparser_transport_selector(args)
    batch = Batch(transport_loop)
    batch.messaging_stack.run()


if __name__ == '__main__':
    main()
