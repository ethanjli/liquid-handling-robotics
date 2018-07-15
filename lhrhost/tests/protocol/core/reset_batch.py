"""Test reset RPC command functionality."""
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
from lhrhost.protocol.core.reset import Printer, Protocol
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
        self.protocol_printer = Printer(prefix=(batch.RESPONSE_PREFIX))
        self.command_printer = MessagePrinter(prefix='  Sending: ')
        self.protocol = Protocol(
            self.messaging_stack.connection_synchronizer,
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
        await asyncio.sleep(1.0)

        print('RPC-style with completion wait:')
        await self.protocol.request_complete()
        await asyncio.sleep(2.0)
        print(batch.RESPONSE_PREFIX + 'Reset completed!')

        print('RPC-style with acknowledgement response wait:')
        await self.protocol.request()
        print(batch.RESPONSE_PREFIX + 'Reset command acknowledged!')
        await self.messaging_stack.connection_synchronizer.disconnected.wait()
        print(batch.RESPONSE_PREFIX + 'Connection lost!')
        await self.messaging_stack.connection_synchronizer.connected.wait()
        print(batch.RESPONSE_PREFIX + 'Reset completed!')
        await asyncio.sleep(2.0)

        await asyncio.sleep(2.0)
        print(batch.OUTPUT_FOOTER)
        print('Quitting...')


def main():
    """Test the reset protocol."""
    parser = argparse.ArgumentParser(
        description='Test the reset protocol.'
    )
    add_argparser_transport_selector(parser)
    args = parser.parse_args()
    transport_loop = parse_argparser_transport_selector(args)
    batch = Batch(transport_loop)
    batch.messaging_stack.run()


if __name__ == '__main__':
    main()
