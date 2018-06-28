"""Version channels of core protocol."""

# Standard imports
from abc import abstractmethod
from functools import total_ordering
from typing import Iterable, List, Optional

# Local package imports
from lhrhost.messaging.presentation import Message
from lhrhost.protocol import (
    ChannelHandlerTreeChildNode, ChannelHandlerTreeNode,
    Command, CommandIssuer
)
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
        if index == 0:
            return self.major
        elif index == 1:
            return self.minor
        elif index == 2:
            return self.patch
        else:
            raise KeyError

    def __len__(self):
        """Return the length of the version tuple."""
        return 3

    def __setitem__(self, index, value):
        """Modify a component of the version."""
        if index == 0:
            self.major = value
        elif index == 1:
            self.minor = value
        elif index == 2:
            self.patch = value
        else:
            raise KeyError

    def __eq__(self, other):
        """Determine whether the version is equal to an other version."""
        return self.tuple == other.tuple

    def __lt__(self, other):
        """Determine whether the version is less than an other version."""
        return self.tuple < other.tuple


# Receipt of Versions

class VersionReceiver(object, metaclass=InterfaceClass):
    """Interface for a class which receives Version/* responses."""

    @abstractmethod
    async def on_version(self, version: Version) -> None:
        """Receive and handle Version/* response."""
        pass


# Type-checking names
_VersionReceivers = Iterable[VersionReceiver]


# Printing

class VersionPrinter(VersionReceiver, Printer):
    """Simple class which prints received Version/* responses."""

    async def on_version(self, version: Version) -> None:
        """Receive and handle a serialized message."""
        self.print('Version {}'.format(version))


class VersionComponentProtocol(ChannelHandlerTreeChildNode, CommandIssuer):
    """Tracks protocol component version."""

    def __init__(self, *args, **kwargs):
        """Initialize member variables."""
        super().__init__(*args, **kwargs)
        self.command_receivers = self.parent.command_receivers

    # Commands

    async def request(self):
        """Send a Version/_ request command to message receivers."""
        message = Message(self.name_path)
        await self.issue_command(Command(message))

    # Implement ChannelHandlerTreeNode

    async def on_received_message(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the node.

        If the full version becomes discovered and is different from what was
        previously recorded, notifies the parent's version receivers.
        """
        if message.payload is None:
            return
        if message.channel == self.name_path:
            previous = self.parent.version[int(self.node_name)]
            new = int(message.payload)
            self.parent.version[int(self.node_name)] = new
            if self.parent.version.known and new != previous:
                await self.parent.notify_version_receivers()
        self.on_response(message.channel)


class VersionProtocol(ChannelHandlerTreeNode, CommandIssuer):
    """Tracks protocol version."""

    def __init__(self, version_receivers: Optional[_VersionReceivers]=None, **kwargs):
        """Initialize member variables."""
        super().__init__(**kwargs)

        self.major = VersionComponentProtocol(self, 'Major', '0', **kwargs)
        self.minor = VersionComponentProtocol(self, 'Minor', '1', **kwargs)
        self.patch = VersionComponentProtocol(self, 'Patch', '2', **kwargs)

        self.version: Version = Version(None, None, None)
        self.__version_receivers: List[VersionReceiver] = []
        if version_receivers:
            self.__version_receivers = [receiver for receiver in version_receivers]

    async def notify_version_receivers(self) -> None:
        """Notify all receivers of received Version response."""
        for receiver in self.__version_receivers:
            await receiver.on_version(self.version)

    # Commands

    async def request(self):
        """Send a Version command to message receivers."""
        message = Message('v')
        wait_channels = ['v0', 'v1', 'v2']
        await self.issue_command(Command(message, wait_channels))

    # Implement ChannelTreeNode

    @property
    def node_channel(self) -> str:
        """Return the channel of the node as a string."""
        return 'Version'

    @property
    def node_name(self) -> str:
        """Return the channel name of the node as a string."""
        return 'v'

    @property
    def children(self):
        """Return a dict of the child ChannelTreeNodes keyed by prefixes."""
        return {
            self.major.node_name: self.major,
            self.minor.node_name: self.minor,
            self.patch.node_name: self.patch
        }

    # Implement ChannelHandlerTreeNode

    async def on_received_message(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the node."""
        if message.payload is None:
            return
        self.on_response(message.channel)
