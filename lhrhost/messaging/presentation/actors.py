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

    def __init__(self, arbiter, get_command_targets, translator, **kwargs):
        """Initialize member variables."""
        super().__init__(arbiter, get_command_targets, **kwargs)
        self._translator = translator

    async def forward_input_line(self, input_line, command_target):
        """Forward the serialized command message to a target."""
        try:
            deserialized = self._translator.deserialize(input_line)
        except InvalidSerializationError:
            logger.error('Malformed message {}'.format(input_line))
            return
        try:
            await ps.send(
                command_target, 'send_serialized_message',
                self._translator.serialize(deserialized)
            )
        except BrokenPipeError:
            pass
