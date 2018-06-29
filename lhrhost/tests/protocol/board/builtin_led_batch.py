"""Test BuiltinLED RPC command functionality."""
# Standard imports
import asyncio
import logging

# Local package imports
from lhrhost.messaging.presentation import BasicTranslator, MessagePrinter
from lhrhost.messaging.transport.actors import ResponseReceiver, TransportManager
from lhrhost.protocol.board.builtin_led import Printer, Protocol
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
        self.protocol_printer = Printer(prefix=batch.RESPONSE_PREFIX)
        self.command_printer = MessagePrinter(prefix='  Sending: ')
        self.protocol = Protocol(
            response_receivers=[self.protocol_printer],
            command_receivers=[self.command_printer]
        )
        self.response_printer = MessagePrinter(prefix=batch.RESPONSE_PREFIX)
        self.translator = BasicTranslator(
            message_receivers=[self.response_printer, self.protocol]
        )
        self.protocol.command_receivers.append(self.translator)
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

        print('RPC-style with empty payloads:')
        await self.protocol.request()
        await self.protocol.blink.request()
        await self.protocol.blink.high_interval.request()
        await self.protocol.blink.low_interval.request()
        await self.protocol.blink.periods.request()
        await self.protocol.blink.notify.request()

        print('RPC with complete wait for finite-periods blink:')
        await self.protocol.blink.notify.request(1)
        await self.protocol.blink.low_interval.request(500)
        await self.protocol.blink.high_interval.request(500)
        await self.protocol.blink.request_complete(5)
        await asyncio.sleep(1.0)

        print('RPC-style manual blink:')
        for i in range(10):
            await self.protocol.request(1)
            await asyncio.sleep(0.25)
            await self.protocol.request(0)
            await asyncio.sleep(0.25)

        print('RPC-style without waiting for blink completion:')
        await self.protocol.blink.notify.request(0)
        await self.protocol.blink.low_interval.request(100)
        await self.protocol.blink.high_interval.request(100)
        await self.protocol.blink.request(1)
        await asyncio.sleep(5.0)

        print(batch.OUTPUT_FOOTER)
        print('Quitting...')


if __name__ == '__main__':
    main(Batch)
