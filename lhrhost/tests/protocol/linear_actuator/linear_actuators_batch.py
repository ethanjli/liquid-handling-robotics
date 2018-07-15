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
from lhrhost.messaging.presentation import MessagePrinter
from lhrhost.protocol.linear_actuator import Printer, Protocol
from lhrhost.tests.messaging.transport.batch import (
    BatchExecutionManager, LOGGING_CONFIG
)
from lhrhost.util import batch

# Logging
logging.config.dictConfig(LOGGING_CONFIG)


class Batch:
    """Actor-based batch execution."""

    def __init__(self, transport_loop):
        """Initialize member variables."""
        self.messaging_stack = MessagingStack(transport_loop)
        self.z_printer = Printer(
            'Z-Axis', prefix=batch.RESPONSE_PREFIX
        )
        self.y_printer = Printer(
            'Y-Axis', prefix=batch.RESPONSE_PREFIX
        )
        self.command_printer = MessagePrinter(prefix='  Sending: ')
        self.z = Protocol(
            'ZAxis', 'z',
            response_receivers=[self.z_printer],
            command_receivers=[self.command_printer]
        )
        self.y = Protocol(
            'YAxis', 'y',
            response_receivers=[self.y_printer],
            command_receivers=[self.command_printer]
        )
        self.response_printer = MessagePrinter(prefix=batch.RESPONSE_PREFIX)
        self.messaging_stack.register_response_receivers(self.response_printer)
        self.messaging_stack.register_response_receivers(self.z)
        self.messaging_stack.register_response_receivers(self.y)
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
        print('Running test routine...')
        await asyncio.gather(self.z.initialized.wait(), self.y.initialized.wait())

        print('Sequential positioning')
        await self.y.feedback_controller.request_complete(720)
        print('  Y-Axis now at {}'.format(self.y.position.last_response_payload))
        await self.z.feedback_controller.request_complete(0)
        print('  Z-Axis now at {}'.format(self.z.position.last_response_payload))
        await self.z.feedback_controller.request_complete(1000)
        print('  Z-Axis now at {}'.format(self.z.position.last_response_payload))
        await self.y.feedback_controller.request_complete(0)
        print('  Y-Axis now at {}'.format(self.y.position.last_response_payload))

        print('Concurrent positioning')
        z_task = self.z.feedback_controller.request_complete(0)
        y_task = self.y.feedback_controller.request_complete(720)
        await asyncio.gather(z_task, y_task)
        print('  Z-Axis now at {}'.format(self.z.position.last_response_payload))
        print('  Y-Axis now at {}'.format(self.y.position.last_response_payload))
        z_task = self.z.feedback_controller.request_complete(1000)
        y_task = self.y.feedback_controller.request_complete(0)
        await asyncio.gather(z_task, y_task)
        print('  Z-Axis now at {}'.format(self.z.position.last_response_payload))
        print('  Y-Axis now at {}'.format(self.y.position.last_response_payload))

        print('Concurrent sequential positioning')

        async def z_sequence():
            for i in range(4):
                await self.z.feedback_controller.request_complete(0)
                print('  Z-Axis now at {}'.format(self.z.position.last_response_payload))
                await self.z.feedback_controller.request_complete(1000)
                print('  Z-Axis now at {}'.format(self.z.position.last_response_payload))

        async def y_sequence():
            for i in range(4):
                await self.y.feedback_controller.request_complete(0)
                print('  Y-Axis now at {}'.format(self.y.position.last_response_payload))
                await self.y.feedback_controller.request_complete(720)
                print('  Y-Axis now at {}'.format(self.y.position.last_response_payload))

        await asyncio.gather(z_sequence(), y_sequence())

        print(batch.OUTPUT_FOOTER)
        print('Quitting...')


def main():
    """Test the linear actuator protocol for two actuators."""
    parser = argparse.ArgumentParser(
        description='Test the linear actuator protocol for two actuators.'
    )
    add_argparser_transport_selector(parser)
    args = parser.parse_args()
    transport_loop = parse_argparser_transport_selector(args)
    batch = Batch(transport_loop)
    batch.messaging_stack.run()


if __name__ == '__main__':
    main()
