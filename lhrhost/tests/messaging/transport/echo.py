"""Test batch execution functionality."""
# Standard imports
import asyncio
import logging

# Local package imports
from lhrhost.messaging.transport import SerializedMessagePrinter
from lhrhost.messaging.transport.actors import BatchExecutionManager, TransportManager
from lhrhost.tests.messaging.transport import console

# External imports
from pulsar.api import arbiter

# Logging
logging.config.dictConfig(console.LOGGING_CONFIG)

LOGGING_CONFIG = console.LOGGING_CONFIG
OUTPUT_WIDTH = console.CONSOLE_WIDTH
OUTPUT_HEADER = console.CONSOLE_HEADER
main = console.main


class BatchExecutionManager(BatchExecutionManager):
    """Class to run a test routine."""

    def __init__(self, arbiter, get_command_targets, test_routine, **kwargs):
        """Initialize member variables."""
        super().__init__(arbiter, get_command_targets, **kwargs)
        self._test_routine = test_routine

    async def on_execution_ready(self):
        """Run the test routine when execution becomes possible."""
        await super().on_execution_ready()
        await self._test_routine()


class Batch:
    """Actor-based batch execution."""

    def __init__(self, transport_loop):
        """Initialize member variables."""
        self.arbiter = arbiter(start=self._start, stopping=self._stop)
        self.response_printer = SerializedMessagePrinter(prefix='\t' * OUTPUT_WIDTH)
        self.command_printer = SerializedMessagePrinter(prefix='  Sending: ')
        self.transport_manager = TransportManager(
            self.arbiter, transport_loop,
            response_receivers=[self.response_printer]
        )
        self.batch_execution_manager = BatchExecutionManager(
            self.arbiter, self.transport_manager.get_actors, self.test_routine,
            header=OUTPUT_HEADER,
            ready_waiter=self.transport_manager.wait_transport_connected
        )

    async def test_routine(self):
        """Run the batch execution test routine."""
        print('Running test routine...')
        await asyncio.sleep(1.0)
        for i in range(10):
            message = '<e>({})'.format(i)
            await self.command_printer.on_serialized_message(message)
            await self.transport_manager.command_sender.on_serialized_message(message)
            await asyncio.sleep(0.5)

    def run(self):
        """Run the batch routine, blocking the caller's thread."""
        self.arbiter.start()

    def _start(self, arbiter):
        """Start the actors and managers."""
        self.transport_manager.start()
        self.batch_execution_manager.start()

    def _stop(self, arbiter):
        """Stop the actors and managers."""
        self.transport_manager.stop()
        self.batch_execution_manager.stop()


if __name__ == '__main__':
    main(Batch)
