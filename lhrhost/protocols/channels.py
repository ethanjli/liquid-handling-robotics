# Standard imports
from abc import abstractmethod

# Local package imports
from lhrhost.serialio.dispatch import MessageReceiver
from lhrhost.util.interfaces import InterfaceClass

class ChannelTreeNode(MessageReceiver, metaclass=InterfaceClass):
    @property
    @abstractmethod
    def node_prefix(self) -> str:
        pass

    def on_received_message(self, subchannel, message):
        pass

    @property
    def subchannel_handlers(self):
        return None

    @property
    def child_nodes(self):
        return None

    def on_message(self, message):
        channel = message.channel
        if not channel.startswith(self.node_prefix):
            return
        subchannel = channel[len(self.node_prefix):]
        self.on_received_message(subchannel, message)
        if self.subchannel_handlers is not None:
            try:
                self.subchannel_handlers[subchannel](subchannel, message)
            except KeyError:
                pass
        if self.child_nodes is not None:
            try:
                pass
                # TODO: dispatch to any child nodes matching as a prefix on subchannel
            except KeyError:
                pass

