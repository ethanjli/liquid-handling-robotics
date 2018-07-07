"""Version channels of core protocol."""

# Standard imports
import asyncio
from abc import abstractmethod
from functools import total_ordering
from typing import Iterable, List, Optional

# Local package imports
from lhrhost.messaging.presentation import Message
from lhrhost.protocol import Command, ProtocolHandlerNode
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

class Receiver(object, metaclass=InterfaceClass):
    """Interface for a class which receives Version/* responses."""

    @abstractmethod
    async def on_version(self, version: Version) -> None:
        """Receive and handle Version/* response."""
        pass


# Type-checking names
_Receivers = Iterable[Receiver]


# Printing

class Printer(Receiver, Printer):
    """Simple class which prints received Version/* responses."""

    async def on_version(self, version: Version) -> None:
        """Receive and handle a serialized message."""
        self.print('Version {}'.format(version))


class ComponentProtocol(ProtocolHandlerNode):
    """Tracks protocol component version."""

    def __init__(self, channel, channel_name, **kwargs):
        """Initialize member variables."""
        super().__init__(channel, channel_name, **kwargs)

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
                await self.parent.notify_response_receivers()


class Protocol(ProtocolHandlerNode):
    """Tracks protocol version."""

    def __init__(self, response_receivers: Optional[_Receivers]=None, **kwargs):
        """Initialize member variables."""
        super().__init__('Version', 'v', **kwargs)

        self.major = ComponentProtocol('Major', '0', parent=self, **kwargs)
        self.minor = ComponentProtocol('Minor', '1', parent=self, **kwargs)
        self.patch = ComponentProtocol('Patch', '2', parent=self, **kwargs)

        self.version: Version = Version(None, None, None)
        self.response_receivers: List[Receiver] = []
        if response_receivers:
            self.response_receivers = [receiver for receiver in response_receivers]

    async def notify_response_receivers(self) -> None:
        """Notify all receivers of received Version response."""
        await asyncio.gather(*[
            receiver.on_version(self.version)
            for receiver in self.response_receivers
        ])

    # Commands

    async def request(self):
        """Send a Version command to message receivers."""
        message = Message('v')
        wait_channels = ['v0', 'v1', 'v2']
        await self.issue_command(Command(message, wait_channels))

    # Implement ProtocolHandlerNode

    @property
    def children_list(self):
        """Return a list of child nodes."""
        return [self.major, self.minor, self.patch]
