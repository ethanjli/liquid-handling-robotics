"""Test version RPC command functionality at console startup."""
# Standard imports
import concurrent
import logging
import asyncio

# Local package imports
from lhrhost.messaging.presentation import BasicTranslator, Message, MessagePrinter
from lhrhost.messaging.transport import SerializedMessagePrinter
from lhrhost.messaging.transport.actors import ConsoleManager, TransportManager
from lhrhost.protocol.core.version import VersionPrinter, VersionProtocol
from lhrhost.tests.messaging.transport import console

# External imports
from pulsar.api import arbiter

# Logging
logging.config.dictConfig(console.LOGGING_CONFIG)


class BatchConsoleManager(ConsoleManager):

    def __init__(self, arbiter, get_command_targets, test_routine, **kwargs):
        """Initialize member variables."""
        super().__init__(arbiter, get_command_targets, **kwargs)
        self._test_routine = test_routine

    async def on_console_ready(self):
        await super().on_console_ready()
        print('Starting test routine')
        await self._test_routine()
        raise KeyboardInterrupt


class Console:
    """Actor-based serial console."""

    def __init__(self, transport_loop):
        """Initialize member variables."""
        self.arbiter = arbiter(start=self._start, stopping=self._stop)
        self.version_printer = VersionPrinter(prefix=(
            '\t' * console.CONSOLE_WIDTH + 'Version: '
        ))
        self.version_protocol = VersionProtocol(
            version_receivers=[self.version_printer]
        )
        self.response_printer = MessagePrinter(prefix='\t' * console.CONSOLE_WIDTH)
        self.command_printer = SerializedMessagePrinter(prefix='  Sending: ')
        self.translator = BasicTranslator(
            message_receivers=[self.response_printer, self.version_protocol],
            serialized_message_receivers=[self.command_printer]
        )
        self.version_protocol.message_receivers.append(self.translator)
        self.transport_manager = TransportManager(
            self.arbiter, transport_loop,
            response_receivers=[self.translator]
        )
        self.translator.serialized_message_receivers.append(self.transport_manager.command_sender)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.console_manager = BatchConsoleManager(
            self.arbiter, self.transport_manager.get_actors, self.test_routine,
            console_header=console.CONSOLE_HEADER,
            executor=self.executor,
            ready_waiter=self.transport_manager.wait_transport_connected
        )

    async def test_routine(self):
        print('Running test routine...')
        await self.translator.on_message(Message('e', 1))
        await asyncio.sleep(1.0)
        await self.translator.on_message(Message('e', 2))
        await asyncio.sleep(1.0)
        await self.translator.on_message(Message('e', 3))
        await asyncio.sleep(1.0)
        await self.translator.on_message(Message('e', 4))
        await asyncio.sleep(1.0)

        self.version_protocol.version.reset()
        print('RPC:')
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

    def run(self):
        """Run the console, blocking the caller's thread."""
        self.arbiter.start()

    def _start(self, arbiter):
        """Start the actors and managers."""
        self.transport_manager.start()
        self.console_manager.start()

    def _stop(self, arbiter):
        """Stop the actors and managers."""
        self.transport_manager.stop()
        self.console_manager.stop()


if __name__ == '__main__':
    console.main(Console)
