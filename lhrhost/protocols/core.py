"""Core protocol functionality."""

# Local package imports
from lhrhost.messaging.presentation import DeserializedMessageReceiver, Message


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
