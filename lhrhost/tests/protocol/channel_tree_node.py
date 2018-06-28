"""Shows some basic examples for protocol.ChannelTreeNode."""

# Standard imports
import asyncio

# Local package imports
from lhrhost.messaging.presentation import Message
from lhrhost.protocol import ChannelHandlerTreeNode


class Child(ChannelHandlerTreeNode):
    def __init__(self, parent):
        self._parent = parent

    @property
    def parent(self):
        return self._parent

    @property
    def node_channel(self):
        return 'Child'

    @property
    def node_name(self):
        return 'c'

    async def on_received_message(self, channel_name_remainder, message):
        print('{} received: {}|{}'.format(
            self.channel_path, channel_name_remainder, message
        ))

    @property
    def child_handlers(self):
        return {
            '1': self.on_received_1_message,
            '2': self.on_received_2_message
        }

    async def on_received_1_message(self, channel_name_remainder, message):
        print('{}/1 received: {}|{}'.format(
            self.channel_path, channel_name_remainder, message
        ))

    async def on_received_2_message(self, channel_name_remainder, message):
        print('{}/2 received: {}|{}'.format(
            self.channel_path, channel_name_remainder, message
        ))


class Root(ChannelHandlerTreeNode):
    def __init__(self):
        self.child = Child(self)

    @property
    def node_channel(self):
        return 'Root'

    @property
    def node_name(self):
        return 'r'

    async def on_received_message(self, channel_name_remainder, message):
        print('{} received: {}|{}'.format(
            self.channel_path, channel_name_remainder, message
        ))

    @property
    def child_handlers(self):
        return {
            '1234': self.on_received_1234_message,
            't': self.on_received_t_message
        }

    @property
    def children(self):
        return {
            self.child.node_name: self.child
        }

    async def on_received_1234_message(self, channel_name_remainder, message):
        print('{}/1234 received: {}|{}'.format(
            self.channel_path, channel_name_remainder, message
        ))

    async def on_received_t_message(self, channel_name_remainder, message):
        print('{}/Test received: {}|{}'.format(
            self.channel_path, channel_name_remainder, message
        ))


async def main():
    """Run some tests of ChannelTreeNode."""
    root = Root()
    child = root.child
    assert root.node_name == 'r'
    assert root.name_path == 'r'
    assert root.node_channel == 'Root'
    assert root.channel_path == 'Root'
    assert child.node_name == 'c'
    assert child.name_path == 'rc'
    assert child.node_channel == 'Child'
    assert child.channel_path == 'Root/Child'
    messages = [
        Message('r', 12345),
        Message('rabcd', 12345),
        Message('r1234', 12345),
        Message('r123456', 12345),
        Message('rt', 12345),
        Message('rt123456', 12345),
        Message('rc', 12345),
        Message('rc1', 12345),
        Message('rc1a', 12345),
        Message('rc2', 12345),
        Message('rc2a', 12345),
    ]
    for message in messages:
        print(message)
        await root.on_message(message)
        print()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
