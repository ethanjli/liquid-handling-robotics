"""Support for the host-peripheral messaging protocol."""

# Local package imports
from lhrhost.messaging.presentation import BasicTranslator
from lhrhost.messaging.transport.actors import ResponseReceiver, TransportManager

# External imports
from pulsar.api import arbiter


class MessagingStack(object):
    """Abstraction layer for the messaging protocol stack."""

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
        self.translator.serialized_message_receivers.append(
            self.transport_manager.command_sender
        )
        self.command_sender = self.transport_manager.command_sender
        self.connection_synchronizer = self.transport_manager.connection_synchronizer
        self.execution_managers = []

    def register_command_senders(self, *command_senders):
        """Register the messaging stack as a command receiver of the given object."""
        for command_sender in command_senders:
            command_sender.command_receivers.append(self.translator)

    def register_response_receivers(self, *response_receivers):
        """Register a message receiver to receive responses over the messaging stack."""
        for response_receiver in response_receivers:
            self.translator.message_receivers.append(response_receiver)

    def register_execution_manager(self, execution_manager):
        """Register an execution manager which can be started or stopped."""
        self.execution_managers.append(execution_manager)

    def run(self):
        """Run the messaging stack, blocking the caller's thread."""
        self.arbiter.start()

    def _start(self, arbiter):
        """Start the messaging stack and execution managers."""
        self.transport_manager.start()
        for execution_manager in self.execution_managers:
            execution_manager.start()

    def _stop(self, arbiter):
        """Stop the messaging stack and execution managers."""
        self.transport_manager.stop()
        for execution_manager in self.execution_managers:
            execution_manager.stop()


def add_argparser_transport_selector(parser):
    """Add a transport-layer implementation selector to an argparse parser."""
    parser.add_argument(
        'transport', choices=['ascii', 'firmata'],
        help='Transport-layer implementation'
    )


def parse_argparser_transport_selector(args):
    """Return a transport loop as specified from the argparse args."""
    if args.transport == 'ascii':
        from lhrhost.messaging.transport.ascii import transport_loop
    elif args.transport == 'firmata':
        from lhrhost.messaging.transport.firmata import transport_loop
    else:
        raise NotImplementedError(
            'Unknown transport-layer implementation: {}'.format(args.transport)
        )
    return transport_loop
