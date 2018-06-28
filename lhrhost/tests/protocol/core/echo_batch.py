"""Test echo RPC command functionality."""
# Standard imports
import asyncio
import logging

# Local package imports
from lhrhost.messaging.presentation import BasicTranslator, MessagePrinter
from lhrhost.messaging.transport.actors import ResponseReceiver, TransportManager
from lhrhost.protocol.core.echo import EchoPrinter, EchoProtocol
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
        self.protocol_printer = EchoPrinter(prefix=(
            batch.RESPONSE_PREFIX + 'Echo: '
        ))
        self.command_printer = MessagePrinter(prefix='  Sending: ')
        self.protocol = EchoProtocol(
            echo_receivers=[self.protocol_printer],
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

        for i in range(10):
            await self.protocol.request_echo(i)
        await asyncio.sleep(1.0)

        print(batch.OUTPUT_FOOTER)
        print('Quitting...')


if __name__ == '__main__':
    main(Batch)
