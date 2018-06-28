"""Interfaces for application-layer protocol implementations."""

# Standard imports
import asyncio
import logging
from abc import abstractmethod
from typing import Dict, Iterable, List, Optional

# Local package imports
from lhrhost.messaging.presentation import Message, MessageReceiver
from lhrhost.util.interfaces import InterfaceClass

# External imports
from multidict import MultiDict

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Type-checking names
_MessageReceivers = Iterable[MessageReceiver]


# Remote-procedure call commands

class Command(object):
    """An asynchronous command.

    If response_channels is None, it is set to be the channel of the message.
    """

    def __init__(
        self, message: Message, response_channels: Optional[Iterable[str]]=None,
        additional_events: Optional[Iterable[asyncio.Event]]=None
    ):
        """Initialize member variables."""
        self.message: Message = message
        self.wait_task: Optional[asyncio.Future] = None
        self._responses_received = MultiDict()
        if response_channels is None:
            response_channels = [message.channel]
        self._responses_received = MultiDict(
            (channel, asyncio.Event()) for channel in response_channels
        )
        self._additional_events: Optional[Iterable[asyncio.Event]] = []
        if additional_events:
            self._additional_events = [event for event in additional_events]

    def on_response(self, channel):
        """Handle a potential response if it matches the right channel."""
        if channel not in self._responses_received:
            return
        for event in self._responses_received.getall(channel):
            if not event.is_set():
                event.set()
                break

    def start_wait_task(self, **kwargs):
        """Start the task to wait for responses to the command."""
        self.wait_task = asyncio.wait(
            (
                [event.wait() for event in self._responses_received.values()] +
                [event.wait() for event in self._additional_events]
            ),
            **kwargs
        )

    def __repr__(self):
        """Represent the command."""
        return 'Command({}, response channels: {})'.format(
            self.message, list(self._responses_received.keys())
        )


class CommandIssuer():
    """Mixin to send and wait for completion of a command to registered receivers."""

    def __init__(self, command_receivers: Optional[_MessageReceivers]=None):
        """Initialize member variables."""
        self.command_receivers: List[MessageReceiver] = []
        if command_receivers:
            self.command_receivers = [receiver for receiver in command_receivers]
        self.__issued_commands: Dict[str, Command] = {}

    def on_response(self, response_channel: str) -> None:
        """Handle a potential response for any issued commands."""
        for (command_channel, command) in self.__issued_commands.items():
            command.on_response(response_channel)

    async def notify_command_receivers(self, command: Command) -> None:
        """Pass the stored version to all registered version receivers.

        Does not wait for responses from any receivers.
        """
        for receiver in self.command_receivers:
            await receiver.on_message(command.message)

    async def issue_command(self, command: Command, cancel_previous=True, **kwargs) -> None:
        """Issue a command and wait for it to complete.

        If there was previously an issued command which has not yet returned,
        wait for it to finish first or cancel it first.
        """
        if command.message.channel in self.__issued_commands:
            prev_command = self.__issued_commands[command.message.channel]
            if prev_command.wait_task is not None:
                if cancel_previous:
                    prev_command.wait_task.cancel()
                else:
                    await self.__issued_commands[command.message.channel].wait_task
        self.__issued_commands[command.message.channel] = command
        # FIXME: there's a potential race condition here
        command.start_wait_task(**kwargs)
        await self.notify_command_receivers(command)
        await command.wait_task
        del self.__issued_commands[command.message.channel]


# Hierarchical channels

class ChannelTreeNode(MessageReceiver, metaclass=InterfaceClass):
    """Mixin for a command handler in a hierarchical handler tree."""

    @property
    def parent(self):
        """Return the parent ChannelTreeNode, if any."""
        return None

    @property
    def children(self):
        """Return a dict of the child ChannelTreeNodes keyed by prefixes, if any."""
        return {}

    @property
    def parents_prefix(self) -> str:
        """Return the prefix string path of the channels above the current channel."""
        if self.parent is None:
            return ''
        else:
            return self.parent.parents_prefix + self.parent.node_prefix

    @property
    @abstractmethod
    def node_prefix(self) -> str:
        """Return the prefix string of the current channel."""
        pass

    def on_received_message(self, channel, subchannel, message):
        """Handle a message recognized as being handled by the node."""
        pass

    @property
    def subchannel_handlers(self):
        """Return a dict of handlers, keyed by their channel paths below current path."""
        return {}

    # Implement MessageReceiver

    async def on_message(self, message):
        """Handle"""
        channel = message.channel
        if not channel.startswith(self.parents_prefix + self.node_prefix):
            return
        subchannel = channel[len(self.node_prefix):]
        self.on_received_message(channel, subchannel, message)

        unhandled = True
        try:
            self.subchannel_handlers[subchannel](channel, subchannel, message)
            unhandled = False
        except KeyError:
            pass
        try:
            for child in self.children.values():
                await child.on_message(message)
            unhandled = False
        except KeyError:
            pass
        if unhandled:
            logger.warn('Unhandled message {}!'.format(message))
