"""Test batch execution functionality."""
# Standard imports
import asyncio
import logging

# Local package imports
from lhrhost.messaging.presentation import BasicTranslator, Message, MessagePrinter
from lhrhost.messaging.transport import SerializedMessagePrinter
from lhrhost.messaging.transport.actors import BatchExecutionManager, TransportManager
from lhrhost.tests.messaging.transport import console

# External imports
from pulsar.api import arbiter

# Logging
logging.config.dictConfig(console.LOGGING_CONFIG)


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


class Console:
    """Actor-based serial console."""

    def __init__(self, transport_loop):
        """Initialize member variables."""
        self.arbiter = arbiter(start=self._start, stopping=self._stop)
        self.response_printer = MessagePrinter(prefix='\t' * console.CONSOLE_WIDTH)
        self.command_printer = SerializedMessagePrinter(prefix='  Sending: ')
        self.translator = BasicTranslator(
            message_receivers=[self.response_printer],
            serialized_message_receivers=[self.command_printer]
        )
        self.transport_manager = TransportManager(
            self.arbiter, transport_loop,
            response_receivers=[self.translator]
        )
        self.translator.serialized_message_receivers.append(self.transport_manager.command_sender)
        self.batch_execution_manager = BatchExecutionManager(
            self.arbiter, self.transport_manager.get_actors, self.test_routine,
            header=console.CONSOLE_HEADER,
            ready_waiter=self.transport_manager.wait_transport_connected
        )

    async def test_routine(self):
        """Run the batch execution test routine."""
        print('Running test routine...')
        await asyncio.sleep(1.0)
        await self.translator.on_message(Message('e', 1))
        await asyncio.sleep(0.5)
        await self.translator.on_message(Message('e', 2))
        await asyncio.sleep(0.5)
        await self.translator.on_message(Message('e', 3))
        await asyncio.sleep(0.5)
        await self.translator.on_message(Message('e', 4))
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
    console.main(Console)
