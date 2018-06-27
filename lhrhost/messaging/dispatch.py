"""Dispatch of messages between serial connections.

This module implements multiplexing/demultiplexing of different message
channels over a single serial connection and dispatch of received messages
to event handlers on the host.
"""

# Standard imports
from collections import defaultdict

# Local package imports
from lhrhost.messaging.presentation import DeserializedMessageReceiver, Message


# Message Dispatch

class Dispatcher(DeserializedMessageReceiver):
    """Dispatcher to demux messages on different channels to their receivers.

    Broadcasts every received message to all receivers registered on the
    channel of the message.

    Attributes:
        receivers (:class:`collections.defaultdict` of :class:`str` to
        :class:`list` of :class:`messaging.presentation.DeserializedMessageReceiver`):
            receivers for messages for each stream, keyed by stream ids. A
            receiver keyed with a stream id of None will receive all messages.

    """

    def __init__(self):
        """Initialize member variables."""
        self.receivers = defaultdict(list)

    # Implement DeserializedMessageReceiver

    def on_message(self, message: Message) -> None:
        """Handle received message."""
        for receiver in self.receivers[message.channel]:
            receiver.on_message(message)
        for receiver in self.receivers[None]:
            receiver.on_message(message)


class MessageEchoer(DeserializedMessageReceiver):
    """Print all received messages."""

    def __init__(self, ignored_channels: set=set()):
        """Initialize member variables."""
        self.ignored_channels = ignored_channels

    # Implement DeserializedMessageReceiver

    def on_message(self, message: Message) -> None:
        """Handle received message."""
        if message.channel not in self.ignored_channels:
            print(message)


class VersionReceiver(DeserializedMessageReceiver):
    """Determines and prints protocol version."""

    def __init__(self):
        """Initialize member variables."""
        self.major_version = None
        self.minor_version = None
        self.patch_version = None

    @property
    def version_known(self) -> None:
        """Determine whether the full protocol version is known."""
        return (
            self.major_version is not None and
            self.minor_version is not None and
            self.patch_version is not None
        )

    def print_version(self) -> None:
        """Print known version."""
        print('Protocol version: {}.{}.{}'.format(
            self.major_version, self.minor_version, self.patch_version
        ))

    # Implement DeserializedMessageReceiver

    def on_message(self, message: Message) -> None:
        """Handle received message."""
        if message.channel == 'v0':
            self.major_version = int(message.payload)
            if self.version_known:
                self.print_version()
        elif message.channel == 'v1':
            self.minor_version = int(message.payload)
            if self.version_known:
                self.print_version()
        elif message.channel == 'v2':
            self.patch_version = int(message.payload)
            if self.version_known:
                self.print_version()
