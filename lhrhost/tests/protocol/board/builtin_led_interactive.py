"""Test BuiltinLED RPC command functionality with an interactive prompt."""
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
from lhrhost.protocol.board.builtin_led import Printer, Protocol
from lhrhost.tests.messaging.transport.batch import (
    BatchExecutionManager, LOGGING_CONFIG
)
from lhrhost.util import batch
from lhrhost.util.cli import Prompt

# External imports
from pulsar.api import arbiter

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
        prompt = Prompt()

        print('Running test routine...')
        await asyncio.sleep(1.0)

        await prompt('Press enter to start blinking:')

        print('Blinking 5 times:')
        await self.protocol.blink.notify.request(1)
        await self.protocol.blink.low_interval.request(250)
        await self.protocol.blink.high_interval.request(250)
        await self.protocol.blink.request_complete(5)

        while True:
            blinks = await prompt('Enter the number of times to blink:')
            try:
                blinks = int(blinks)
                if blinks <= 0:
                    raise ValueError
                break
            except ValueError:
                print('Invalid input!')

        print('Blinking {} times:'.format(blinks))
        await self.protocol.blink.notify.request(1)
        await self.protocol.blink.request_complete(blinks)

        await self.protocol.blink.notify.request(0)
        asyncio.ensure_future(self.protocol.blink.request(1))
        await prompt(
            'Blinking indefinitely. Press enter to stop blinking, '
            'turn the LED on, and exit:'
        )
        await self.protocol.request(1)

        print(batch.OUTPUT_FOOTER)
        print('Quitting...')


def main():
    """Test the built-in LED protocol with an interactive prompt."""
    parser = argparse.ArgumentParser(
        description='Test the built-in LED protocol with an interactive prompt.'
    )
    add_argparser_transport_selector(parser)
    args = parser.parse_args()
    transport_loop = parse_argparser_transport_selector(args)
    batch = Batch(transport_loop)
    batch.messaging_stack.run()


if __name__ == '__main__':
    main()
