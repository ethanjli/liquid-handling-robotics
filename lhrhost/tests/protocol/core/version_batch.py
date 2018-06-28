"""Test version RPC command functionality."""
# Standard imports
import asyncio
import logging

# Local package imports
from lhrhost.messaging.presentation import BasicTranslator, MessagePrinter
from lhrhost.messaging.transport.actors import ResponseReceiver, TransportManager
from lhrhost.protocol.core.version import VersionPrinter, VersionProtocol
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
        self.version_printer = VersionPrinter(prefix=(
            batch.RESPONSE_PREFIX + 'Version: '
        ))
        self.command_printer = MessagePrinter(prefix='  Sending: ')
        self.version_protocol = VersionProtocol(
            version_receivers=[self.version_printer],
            command_receivers=[self.command_printer]
        )
        self.response_printer = MessagePrinter(prefix=batch.RESPONSE_PREFIX)
        self.translator = BasicTranslator(
            message_receivers=[self.response_printer, self.version_protocol]
        )
        self.version_protocol.message_receivers.append(self.translator)
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

        print('RPC-style:')
        self.version_protocol.version.reset()
        print('  Version full')
        await self.version_protocol.request_wait_full()
        self.version_protocol.version.reset()
        print('  Version major')
        await self.version_protocol.request_wait_major()
        print('  Version minor')
        await self.version_protocol.request_wait_minor()
        print('  Version patch')
        await self.version_protocol.request_wait_patch()
        self.version_protocol.version.reset()

        print('Nowait:')
        print('  Version full')
        await self.version_protocol.request_full()
        print('  Version major')
        await self.version_protocol.request_major()
        print('  Version minor')
        await self.version_protocol.request_minor()
        print('  Version patch')
        await self.version_protocol.request_patch()

        await asyncio.sleep(1.0)


if __name__ == '__main__':
    main(Batch)
