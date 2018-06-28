"""Test reset RPC command functionality."""
# Standard imports
import asyncio
import logging

# Local package imports
from lhrhost.messaging.presentation import BasicTranslator, MessagePrinter
from lhrhost.messaging.transport.actors import ResponseReceiver, TransportManager
from lhrhost.protocol.core.reset import ResetPrinter, ResetProtocol
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

        self.translator = BasicTranslator()

        self.response_receiver = ResponseReceiver(
            response_receivers=[self.translator]
        )
        self.transport_manager = TransportManager(
            self.arbiter, transport_loop, response_receiver=self.response_receiver
        )
        self.batch_execution_manager = BatchExecutionManager(
            self.arbiter, self.transport_manager.command_sender, self.test_routine,
            header=batch.OUTPUT_HEADER,
            ready_waiter=self.transport_manager.connection_synchronizer.wait_connected
        )

        self.reset_printer = ResetPrinter(prefix=(batch.RESPONSE_PREFIX))
        self.command_printer = MessagePrinter(prefix='  Sending: ')
        self.reset_protocol = ResetProtocol(
            self.transport_manager.connection_synchronizer,
            reset_receivers=[self.reset_printer],
            command_receivers=[self.command_printer, self.translator]
        )
        self.response_printer = MessagePrinter(prefix=batch.RESPONSE_PREFIX)

        self.translator.message_receivers.append(self.response_printer)
        self.translator.message_receivers.append(self.reset_protocol)
        self.translator.serialized_message_receivers.append(
            self.transport_manager.command_sender
        )

    async def test_routine(self):
        """Run the batch execution test routine."""
        print('Running test routine...')
        await asyncio.sleep(1.0)

        print('RPC-style with completion wait:')
        await self.reset_protocol.request_complete_reset()
        await asyncio.sleep(2.0)
        print(batch.RESPONSE_PREFIX + 'Reset completed!')

        print('RPC-style with acknowledgement response wait:')
        await self.reset_protocol.request_reset()
        print(batch.RESPONSE_PREFIX + 'Reset command acknowledged!')
        await self.transport_manager.connection_synchronizer.disconnected.wait()
        print(batch.RESPONSE_PREFIX + 'Connection lost!')
        await self.transport_manager.connection_synchronizer.connected.wait()
        print(batch.RESPONSE_PREFIX + 'Reset completed!')
        await asyncio.sleep(2.0)

        await asyncio.sleep(2.0)
        print(batch.OUTPUT_FOOTER)
        print('Quitting...')


if __name__ == '__main__':
    main(Batch)
