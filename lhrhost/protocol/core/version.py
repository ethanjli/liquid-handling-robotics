"""Version channels of core protocol."""

# Standard imports
from abc import abstractmethod
from functools import total_ordering
from typing import Iterable, List, Optional

# Local package imports
from lhrhost.messaging.presentation import Message, MessageReceiver
from lhrhost.protocol import Command, CommandIssuer
from lhrhost.util.interfaces import InterfaceClass
from lhrhost.util.printing import Printer


# Versions

@total_ordering
class Version(object):
    """Represent a version."""

    def __init__(self, major=None, minor=None, patch=None):
        """Initialize member variables."""
        self.major = major
        self.minor = minor
        self.patch = patch

    def reset(self) -> None:
        """Reset the version."""
        self.major = None
        self.minor = None
        self.patch = None

    @property
    def known(self) -> bool:
        """Determine whether the full protocol version is known."""
        return (
            self.major is not None and
            self.minor is not None and
            self.patch is not None
        )

    @property
    def tuple(self):
        """Get a tuple representation of the version."""
        return (self.major, self.minor, self.patch)

    def __repr__(self):
        """Return a string representation of the version."""
        return '{}.{}.{}'.format(*self.tuple)

    def __getitem__(self, index):
        """Access a component of the version."""
        return self.tuple[index]

    def __eq__(self, other):
        """Determine whether the version is equal to an other version."""
        return self.tuple == other.tuple

    def __lt__(self, other):
        """Determine whether the version is less than an other version."""
        return self.tuple < other.tuple


# Receipt of Versions

class VersionReceiver(object, metaclass=InterfaceClass):
    """Interface for a class which receives :class:`Version`s.

    This may include versions from self or from other sources.
    """

    @abstractmethod
    def on_version(self, version: Version) -> None:
        """Receive and handle a (deserialized) message, i.e. a :class:`Message`."""
        pass


# Type-checking names
_VersionReceivers = Iterable[VersionReceiver]


# Printing

class VersionPrinter(VersionReceiver, Printer):
    """Simple class which prints received serialized messages."""

    def on_version(self, version: Version) -> None:
        """Receive and handle a serialized message."""
        self.print('Version {}'.format(version))


class VersionProtocol(MessageReceiver, CommandIssuer):
    """Determines and prints protocol version."""

    def __init__(self, version_receivers: Optional[_VersionReceivers]=None, **kwargs):
        """Initialize member variables."""
        super().__init__(**kwargs)
        self.version: Version = Version(None, None, None)
        self.__previous_version: Version = Version(None, None, None)
        self.__version_receivers: List[VersionReceiver] = []
        if version_receivers:
            self.__version_receivers = [receiver for receiver in version_receivers]

    def notify_version_receivers(self) -> None:
        """Pass the stored version to all registered version receivers."""
        for receiver in self.__version_receivers:
            receiver.on_version(self.version)

    # Commands

    async def request_full(self):
        """Send a full version request command to message receivers."""
        await self.notify_message_receivers(Message('v'))

    async def request_major(self):
        """Send a major version component request command to message receivers."""
        await self.notify_message_receivers(Message('v0'))

    async def request_minor(self):
        """Send a minor version component request command to message receivers."""
        await self.notify_message_receivers(Message('v1'))

    async def request_patch(self):
        """Send a patch version component request command to message receivers."""
        await self.notify_message_receivers(Message('v2'))

    async def request_wait_full(self):
        """Send a full version request command to message receivers."""
        await self.issue_command(Command(Message('v'), ['v0', 'v1', 'v2']))

    async def request_wait_major(self):
        """Send a major version component request command to message receivers."""
        await self.issue_command(Command(Message('v0'), ['v0']))

    async def request_wait_minor(self):
        """Send a minor version component request command to message receivers."""
        await self.issue_command(Command(Message('v1'), ['v1']))

    async def request_wait_patch(self):
        """Send a patch version component request command to message receivers."""
        await self.issue_command(Command(Message('v2'), ['v2']))

    # Implement DeserializedMessageReceiver

    async def on_message(self, message: Message) -> None:
        """Handle received message.

        Only handles known version messages. If all components of the version
        have been received and the version is differently than what was previously
        stored, forwards the full version to version receivers.
        """
        if message.payload is None:
            return
        if message.channel == 'v0':
            self.version.major = int(message.payload)
            if self.version.known and self.version != self.__previous_version:
                self.notify_version_receivers()
        elif message.channel == 'v1':
            self.version.minor = int(message.payload)
            if self.version.known and self.version != self.__previous_version:
                self.notify_version_receivers()
        elif message.channel == 'v2':
            self.version.patch = int(message.payload)
            if self.version.known and self.version != self.__previous_version:
                self.notify_version_receivers()
        self.on_response(message.channel)
        self.__previous_version = Version(*self.version)
