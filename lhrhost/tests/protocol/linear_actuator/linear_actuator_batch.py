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
        self.protocol_printer = Printer(
            'Z-Axis', prefix=batch.RESPONSE_PREFIX
        )
        self.command_printer = MessagePrinter(prefix='  Sending: ')
        self.protocol = Protocol(
            'ZAxis', 'z',
            response_receivers=[self.protocol_printer],
            command_receivers=[self.command_printer]
        )
        self.response_printer = MessagePrinter(prefix=batch.RESPONSE_PREFIX)
        self.messaging_stack.register_response_receivers(self.response_printer)
        self.messaging_stack.register_response_receivers(self.protocol)
        self.messaging_stack.register_command_senders(self.protocol)
        self.batch_execution_manager = BatchExecutionManager(
            self.messaging_stack.arbiter, self.messaging_stack.command_sender,
            self.test_routine, header=batch.OUTPUT_HEADER,
            ready_waiter=self.messaging_stack.connection_synchronizer.wait_connected
        )
        self.messaging_stack.register_execution_manager(self.batch_execution_manager)

    async def test_routine(self):
        """Run the batch execution test routine."""
        print('Running test routine...')
        await self.protocol.initialized.wait()

        print('RPC-style with empty payloads:')
        await self.protocol.request()
        await self.protocol.position.request()
        await self.protocol.smoothed_position.request()
        await self.protocol.motor.request()

        print('Recursive request through handler tree with empty payloads:')
        await self.protocol.request_all()

        print('Motor direct duty control')
        # Test basic motor direct duty control
        await self.protocol.motor.request_complete(-255)
        await self.protocol.motor.request_complete(255)
        await self.protocol.motor.request_complete(-100)
        # Test motor polarity setting
        await self.protocol.motor.motor_polarity.request(-1)
        await self.protocol.motor.request_complete(-150)
        await self.protocol.motor.motor_polarity.request(1)
        await self.protocol.motor.request_complete(-100)
        # Test timer timeout
        await self.protocol.motor.timer_timeout.request(200)
        for i in range(10):
            await self.protocol.motor.request_complete(150)
            await asyncio.sleep(0.4)
        await self.protocol.motor.timer_timeout.request(10000)

        print('Motor direct duty control with position notification')
        await self.protocol.position.notify.change_only.request(0)
        task = self.protocol.position.notify.request_complete_time_interval(20, 100)
        await asyncio.sleep(1.0)
        await self.protocol.motor.request(-80)
        await task

        print('Motor position feedback control with position and motor duty notification')
        await self.protocol.position.notify.change_only.request(1)
        await self.protocol.position.notify.interval.request(100)
        await self.protocol.motor.notify.change_only.request(1)
        await self.protocol.motor.notify.interval.request(100)
        await self.protocol.position.notify.request(2)
        await self.protocol.motor.notify.request(2)
        await self.protocol.feedback_controller.request_complete(1000)
        await self.protocol.feedback_controller.request_complete(0)
        await self.protocol.position.notify.request(0)
        await self.protocol.motor.notify.request(0)

        print(batch.OUTPUT_FOOTER)
        print('Quitting...')


def main():
    """Test the linear actuator protocol for a single actuator."""
    parser = argparse.ArgumentParser(
        description='Test the linear actuator protocol for a single actuator.'
    )
    add_argparser_transport_selector(parser)
    args = parser.parse_args()
    transport_loop = parse_argparser_transport_selector(args)
    batch = Batch(transport_loop)
    batch.messaging_stack.run()


if __name__ == '__main__':
    main()
