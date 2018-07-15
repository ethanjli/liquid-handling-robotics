"""Test IOPins RPC command functionality."""
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
from lhrhost.protocol.board.io_pins import Printer, Protocol
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
        self.protocol_printer = Printer(prefix=batch.RESPONSE_PREFIX)
        self.command_printer = MessagePrinter(prefix='  Sending: ')
        self.protocol = Protocol(
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

        for i in range(4):
            await self.protocol.analog.request(i)
        for i in range(2, 14):
            await self.protocol.digital.request(i)
        await asyncio.sleep(1.0)

        print(batch.OUTPUT_FOOTER)
        print('Quitting...')


def main():
    """Test the IO pins protocol."""
    parser = argparse.ArgumentParser(
        description='Test the IO pins protocol'
    )
    add_argparser_transport_selector(parser)
    args = parser.parse_args()
    transport_loop = parse_argparser_transport_selector(args)
    batch = Batch(transport_loop)
    batch.messaging_stack.run()


if __name__ == '__main__':
    main()
