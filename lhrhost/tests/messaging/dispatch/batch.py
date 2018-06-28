"""Test batch execution functionality."""
# Standard imports
import asyncio
import logging

# Local package imports
from lhrhost.messaging.dispatch import Dispatcher
from lhrhost.messaging.presentation import BasicTranslator, Message, MessagePrinter
from lhrhost.messaging.transport.actors import ResponseReceiver, TransportManager
from lhrhost.tests.messaging.transport.batch import (
    Batch, BatchExecutionManager, LOGGING_CONFIG, main
)
from lhrhost.util import batch

# External imports
from pulsar.api import arbiter

# Logging
logging.config.dictConfig(LOGGING_CONFIG)


class Batch(Batch):
    """Actor-based batch execution."""

    def __init__(self, transport_loop):
        """Initialize member variables."""
        self.arbiter = arbiter(start=self._start, stopping=self._stop)
        self.command_printer = MessagePrinter(prefix='  Sending: ')
        self.echo_response_printer = MessagePrinter(
            prefix=('\t' * batch.OUTPUT_WIDTH + '[Echo]\t')
        )
        self.reset_response_printer = MessagePrinter(
            prefix=('\t' * batch.OUTPUT_WIDTH + '[Reset]\t')
        )
        self.version_response_printer = MessagePrinter(
            prefix=('\t' * batch.OUTPUT_WIDTH + '[Version]\t')
        )
        self.builtin_led_response_printer = MessagePrinter(
            prefix=('\t' * batch.OUTPUT_WIDTH + '[BuiltinLED]\t')
        )
        self.response_dispatcher = Dispatcher(
            receivers={
                'e': [self.echo_response_printer],
                'r': [self.reset_response_printer]
            },
            prefix_receivers={
                'v': [self.version_response_printer],
                'l': [self.builtin_led_response_printer],
            }
        )
        self.translator = BasicTranslator(
            message_receivers=[self.response_dispatcher]
        )
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
        print('Running test routine...')
        await asyncio.sleep(1.0)
        for i in range(10):
            message = Message('e', i)
            await self.command_printer.on_message(message)
            await self.translator.on_message(message)
            await asyncio.sleep(0.5)

        print(batch.OUTPUT_FOOTER)
        print('Quitting...')


if __name__ == '__main__':
    main(Batch)
