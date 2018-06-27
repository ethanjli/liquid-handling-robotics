"""Exposes a command-line serial console to the peripheral, with command validation."""
# Standard imports
import concurrent
import logging

# Local package imports
from lhrhost.messaging.presentation import (
    BasicTranslator, MessagePrinter
)
from lhrhost.messaging.presentation.actors import ConsoleManager
from lhrhost.messaging.transport.actors import TransportManager
from lhrhost.tests.messaging.transport import console

# External imports
from pulsar.api import arbiter

# Logging
logging.config.dictConfig(console.LOGGING_CONFIG)


class Console(console.Console):
    """Actor-based serial console."""

    def __init__(self, transport_loop):
        """Initialize member variables."""
        self.arbiter = arbiter(start=self._start, stopping=self._stop)
        self.response_printer = MessagePrinter(
            prefix=('\t' * console.CONSOLE_WIDTH)
        )
        self.translator = BasicTranslator(
            message_receivers=[self.response_printer]
        )
        self.transport_manager = TransportManager(
            self.arbiter, transport_loop,
            response_receivers=[self.translator]
        )
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.console_manager = ConsoleManager(
            self.arbiter, self.transport_manager.get_actors, self.translator,
            console_header=console.CONSOLE_HEADER, executor=self.executor,
            ready_waiter=self.transport_manager.wait_transport_connected
        )


if __name__ == '__main__':
    console.main(Console)
