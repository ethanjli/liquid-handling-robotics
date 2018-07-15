"""Test the presentation layer."""
# Standard imports
import argparse
import asyncio
import logging

# Local package imports
from lhrhost.messaging import (
    MessagingStack,
    add_argparser_transport_selector, parse_argparser_transport_selector
)
from lhrhost.messaging.presentation import Message, MessagePrinter
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
        self.command_printer = MessagePrinter(prefix='  Sending: ')
        self.response_printer = MessagePrinter(prefix=batch.RESPONSE_PREFIX)
        self.messaging_stack.register_response_receivers(self.response_printer)
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
        for i in range(10):
            message = Message('e', i)
            await self.command_printer.on_message(message)
            await self.messaging_stack.translator.on_message(message)
            await asyncio.sleep(0.5)

        print(batch.OUTPUT_FOOTER)
        print('Quitting...')


def main():
    """Test the presentation layer."""
    parser = argparse.ArgumentParser(
        description='Test the presentation layer.'
    )
    add_argparser_transport_selector(parser)
    args = parser.parse_args()
    transport_loop = parse_argparser_transport_selector(args)
    batch = Batch(transport_loop)
    batch.messaging_stack.run()


if __name__ == '__main__':
    main()
