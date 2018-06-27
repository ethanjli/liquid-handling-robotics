"""Exposes a command-line serial console to the peripheral, with command validation."""
# Standard imports
import concurrent
import logging

# Local package imports
from lhrhost.messaging.dispatch import Dispatcher
from lhrhost.messaging.presentation import (
    BasicTranslator, MessagePrinter
)
from lhrhost.messaging.presentation.actors import ConsoleManager
from lhrhost.messaging.transport import SerializedMessagePrinter
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
        self.echo_response_printer = MessagePrinter(
            prefix=('\t' * console.CONSOLE_WIDTH),
            suffix=(' [Echo] \n')
        )
        self.version_response_printer = MessagePrinter(
            prefix=('\t' * console.CONSOLE_WIDTH),
            suffix=(' [Version] \n')
        )
        self.builtin_led_response_printer = MessagePrinter(
            prefix=('\t' * console.CONSOLE_WIDTH),
            suffix=(' [BuiltinLED] \n')
        )
        self.response_dispatcher = Dispatcher(
            receivers={
                'e': [self.echo_response_printer]
            },
            prefix_receivers={
                'v': [self.version_response_printer],
                'l': [self.builtin_led_response_printer],
            }
        )
        self.command_printer = SerializedMessagePrinter(
            prefix='Sending command: '
        )
        self.translator = BasicTranslator(
            message_receivers=[self.response_dispatcher],
            serialized_message_receivers=[self.command_printer]
        )
        self.transport_manager = TransportManager(
            self.arbiter, transport_loop,
            transport_kwargs={
                'serialized_message_receivers': [self.translator]
            }
        )
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.console_manager = ConsoleManager(
            self.arbiter, lambda: [self.transport_manager.actor], self.translator,
            console_header=console.CONSOLE_HEADER,
            executor=self.executor,
            ready_waiter=self.transport_manager.wait_transport_connected
        )


if __name__ == '__main__':
    console.main(Console)
