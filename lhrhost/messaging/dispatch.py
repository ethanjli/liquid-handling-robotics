"""Dispatch of messages between serial connections.

This module implements multiplexing/demultiplexing of different application-layer
message channels over the presentation layer, and dispatch of received messages
from the presentation layer to application-layer receivers.
"""

# Standard imports
import asyncio
from collections import defaultdict
from typing import Dict, List, Optional

# Local package imports
from lhrhost.messaging.presentation import Message, MessageReceiver


# Type-checking names
_MessageReceivers = List[MessageReceiver]
_MessageReceiversTable = Dict[str, _MessageReceivers]


# Message Dispatch

class Dispatcher(MessageReceiver):
    """Dispatcher to demux messages on different channels to their receivers.

    Broadcasts every received message to all receivers registered on the
    channel of the message.

    Attributes:
        receivers (:class:`collections.defaultdict` of :class:`str` to
        :class:`list` of :class:`messaging.presentation.MessageReceiver`):
            receivers for messages for each channel, keyed by channel names. A
            receiver keyed with a channel name of None will receive all messages.
        prefix_receivers (:class:`collections.defaultdict` of :class:`str` to
        :class:`list` of :class:`MessageReceiver`):
            receivers for messages for each channel, keyed by channel name prefixes.
            A receiver keyed with a some prefix will receive all messages on all
            channels whose names start with that prefix.
            A receiver keyed with a empty string prefix will receive all messages.

    """

    def __init__(
        self,
        receivers: Optional[_MessageReceiversTable]=None,
        prefix_receivers: Optional[_MessageReceiversTable]=None,
    ):
        """Initialize member variables."""
        self.__receivers = defaultdict(list)
        if receivers is not None:
            for (channel_name, channel_receivers) in receivers.items():
                for receiver in channel_receivers:
                    self.__receivers[channel_name].append(receiver)
        self.__prefix_receivers = defaultdict(list)
        if prefix_receivers is not None:
            for (channel_name, channel_receivers) in prefix_receivers.items():
                for receiver in channel_receivers:
                    self.__prefix_receivers[channel_name].append(receiver)

    @property
    def message_receivers(self) -> _MessageReceiversTable:
        """Return an iterable of objects to forward received messages to."""
        return self.__receivers

    @property
    def prefix_message_receivers(self) -> _MessageReceiversTable:
        """Return an iterable of objects to forward received messages to."""
        return self.__prefix_receivers

    # Implement MessageReceiver

    async def on_message(self, message: Message) -> None:
        """Handle received message."""
        tasks = []
        for receiver in self.__receivers[message.channel]:
            tasks.append(receiver.on_message(message))
        for receiver in self.__receivers[None]:
            tasks.append(receiver.on_message(message))
        for (prefix, receivers) in self.__prefix_receivers.items():
            if message.channel.startswith(prefix):
                for receiver in receivers:
                    tasks.append(receiver.on_message(message))
        await asyncio.gather(*tasks)
