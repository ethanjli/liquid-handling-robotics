"""Actors for the presentation layer."""

# Standard imports
import logging

# Local package imports
from lhrhost.messaging.presentation import InvalidSerializationError
from lhrhost.messaging.transport import actors

# External imports
import pulsar.api as ps

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ConsoleManager(actors.ConsoleManager):
    """Class to pass console input as send_serialized_message actor commands.

    Creates an asynchronous coroutine which reads lines from stdin on a separate
    thread and handles them by sending them to actors. Lines are passed in a
    round trip through the specified translator first, to ensure they are well-formed.

    This can be used to send lines on stdin as message packets to the actor for
    a transport-layer connection to a peripheral, for example.

    We don't put this in a separate actor - that fails because stdin
    on a separate actor only receives EOF for some reason.
    """

    def __init__(self, arbiter, command_sender, translator, **kwargs):
        """Initialize member variables."""
        super().__init__(arbiter, command_sender, **kwargs)
        self._translator = translator

    async def handle_console_input(self, input_line):
        """Take action based on the provided input.

        Raise KeyboardInterrupt when the input specifies that the console needs to
        stop running. Empty input is a signal to quit.
        """
        if not input_line:
            raise KeyboardInterrupt
        try:
            deserialized = self._translator.deserialize(input_line)
        except InvalidSerializationError:
            logger.error('Malformed message {}'.format(input_line))
            return
        await self.command_sender.on_serialized_message(
            self._translator.serialize(deserialized)
        )
