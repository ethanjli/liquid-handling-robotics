"""Interfaces for application-layer protocol implementations."""

# Standard imports
import asyncio
import logging
from abc import abstractmethod
from typing import Any, Dict, Iterable, List, Optional

# Local package imports
from lhrhost.messaging.presentation import Message, MessageReceiver
from lhrhost.util.interfaces import InterfaceClass, cached_property

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
        await asyncio.gather(*[
            receiver.on_message(command.message)
            for receiver in self.command_receivers
        ])

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

class ChannelTreeNode(metaclass=InterfaceClass):
    """Mixin for anything coresponding to a node in a hierarchical channel tree."""

    @property
    def parent(self):
        """Return the parent ChannelTreeNode, if any."""
        return None

    @property
    def children(self):
        """Return a dict of the child ChannelTreeNodes keyed by prefixes, if any."""
        return {}

    @property
    @abstractmethod
    def node_channel(self) -> str:
        """Return the channel of the node as a string."""
        pass

    @cached_property
    def channel_path(self) -> str:
        """Return the full channel path of the node as a string."""
        if self.parent is None:
            return self.node_channel
        return '{}/{}'.format(self.parent.channel_path, self.node_channel)

    @property
    @abstractmethod
    def node_name(self) -> str:
        """Return the channel name of the node as a string."""
        pass

    @cached_property
    def name_path(self) -> str:
        """Return the channel name of the node as a string."""
        if self.parent is None:
            return self.node_name
        return '{}{}'.format(self.parent.name_path, self.node_name)


class ChannelHandlerTreeNode(ChannelTreeNode, MessageReceiver, metaclass=InterfaceClass):
    """Mixin for a command handler in a hierarchical handler tree."""

    async def on_any_message(self, message):
        """Handle any message whether or not it is recognized as by the node."""
        pass

    async def on_received_message(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the node."""
        pass

    @property
    def child_prefix_handlers(self):
        """Return a dict of handlers, keyed by channel path prefixes below current path."""
        return {}

    @property
    def child_handlers(self):
        """Return a dict of handlers, keyed by channel paths below current path."""
        return {}

    # Implement MessageReceiver

    async def on_message(self, message):
        """Receive and handle a message by dispatching it to the appropriate handler."""
        channel_name = message.channel
        await self.on_any_message(message)
        if not channel_name.startswith(self.name_path):
            return
        channel_name_remainder = channel_name[len(self.name_path):]
        await self.on_received_message(channel_name_remainder, message)

        try:
            await self.child_handlers[channel_name_remainder](
                channel_name_remainder, message
            )
        except KeyError:
            pass
        tasks = []
        for (channel_name_remainder_prefix, handler) in self.child_prefix_handlers.items():
            if channel_name_remainder.startswith(channel_name_remainder_prefix):
                tasks.append(handler(channel_name_remainder, message))
        for child in self.children.values():
            tasks.append(child.on_message(message))
        await asyncio.gather(*tasks)


class ProtocolHandlerNode(ChannelHandlerTreeNode, CommandIssuer):
    """Mixin for a non-root command handler in a hierarchical handler tree."""

    # TODO:implement feedbackcontroller nodes

    def __init__(self, node_channel, node_name, parent=None, **kwargs):
        """Initialize member variables."""
        super().__init__(**kwargs)
        self._parent = parent
        self._node_channel = node_channel
        self._node_name = node_name
        self.last_response_payload = None
        if self.parent is not None:
            self.command_receivers = self.parent.command_receivers

    async def notify_response_receivers(self, payload: Any) -> None:
        """Validate the payload and notify the response receivers."""
        if payload is None:
            logger.warn(
                'Received response {} with an empty payload. This should not '
                'happen, and the response has been ignored.'.format(payload)
            )
            return
        result = self.transform_response_payload(payload)
        if result is None:
            return
        notifiers = [
            self.get_response_notifier(receiver) for receiver in self.response_receivers
        ]
        notifiers = [notifier for notifier in notifiers if notifier is not None]
        await asyncio.gather(*[notifier(*result) for notifier in notifiers])

    def transform_response_payload(self, payload) -> Optional[Iterable[Any]]:
        """Transform the payload into a list of args for the response receiver's method.

        The list of args will be unpacked in the response receiver's method, which
        is specified by get_response_notifier. Return None to avoid notifying any
        receivers.
        """
        return (payload,)

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response.

        Return None to avoid notifying any receivers.
        """
        return None

    @property
    def children_list(self):
        """Return a list of child nodes."""
        return []

    async def request_all(self):
        """Recursively attempt to call the request method with an empty payload."""
        if callable(getattr(self, 'request', None)):
            await self.request()
        for child in self.children_list:
            await child.request_all()

    # Implement ChannelTreeNode

    @property
    def parent(self):
        """Return the parent ChannelTreeNode."""
        return self._parent

    @cached_property
    def children(self):
        """Return a dict of the child ChannelTreeNodes keyed by prefixes, if any."""
        return {child.node_name: child for child in self.children_list}

    @property
    def node_channel(self) -> str:
        """Return the channel of the node as a string."""
        return self._node_channel

    @property
    def node_name(self) -> str:
        """Return the channel name of the node as a string."""
        return self._node_name

    async def on_any_message(self, message):
        """Handle any message whether or not it is recognized as by the node."""
        if message.payload is None:
            return
        self.on_response(message.channel)

    async def on_received_message(self, channel_name_remainder, message) -> None:
        """Handle received message."""
        if message.payload is None:
            return
        if message.channel == self.name_path:
            if message.payload is not None:
                self.last_response_payload = message.payload
            await self.notify_response_receivers(message.payload)
