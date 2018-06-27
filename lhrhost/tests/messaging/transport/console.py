"""Exposes a command-line serial console to the peripheral."""
# Standard imports
import argparse
import concurrent
import logging

# Local package imports
from lhrhost.messaging.transport import SerializedMessagePrinter
from lhrhost.messaging.transport.actors import ConsoleManager, TransportManager

# External imports
from pulsar.api import arbiter
from pulsar.utils.log import LOGGING_CONFIG

# Logging
LOGGING_CONFIG['formatters']['simple']['format'] = (
    '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
LOGGING_CONFIG['handlers']['console']['formatter'] = 'simple'
LOGGING_CONFIG['loggers']['pulsar'] = {'level': 'ERROR'}
logging.config.dictConfig(LOGGING_CONFIG)

CONSOLE_WIDTH = 8
CONSOLE_HEADER = (
    'Commands' + ('\t' * (CONSOLE_WIDTH - 1)) + 'Responses' + '\n' +
    ('-' * 12 * CONSOLE_WIDTH)
)


class Console:
    """Actor-based serial console."""

    def __init__(self, transport_loop):
        """Initialize member variables."""
        self.arbiter = arbiter(start=self._start, stopping=self._stop)
        self.response_printer = SerializedMessagePrinter(
            prefix=('\t' * CONSOLE_WIDTH)
        )
        self.transport_manager = TransportManager(
            self.arbiter, transport_loop,
            response_receivers=[self.response_printer]
        )
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.console_manager = ConsoleManager(
            self.arbiter, self.transport_manager.get_actors,
            console_header=CONSOLE_HEADER, executor=self.executor,
            ready_waiter=self.transport_manager.wait_transport_connected
        )

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


def main(Console):
    """Run a serial console using the selected transport-layer implementation."""
    parser = argparse.ArgumentParser(
        description='Send and receive transport-layer data with a command-line console.'
    )
    parser.add_argument(
        'transport', choices=['ascii', 'firmata'],
        help='Transport-layer implementation.'
    )
    args = parser.parse_args()
    if args.transport == 'ascii':
        from lhrhost.messaging.transport.ascii import transport_loop
    elif args.transport == 'firmata':
        from lhrhost.messaging.transport.firmata import transport_loop
    else:
        raise NotImplementedError(
            'Unknown transport layer implementation: {}'.format(transport_loop)
        )
    console = Console(transport_loop)
    console.run()


if __name__ == '__main__':
    main(Console)
