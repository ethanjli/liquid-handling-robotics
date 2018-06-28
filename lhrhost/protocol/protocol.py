"""Interfaces for application-layer protocol implementations."""

# Standard imports
import asyncio
from typing import Dict, Iterable, List, Optional

# Local package imports
from lhrhost.messaging.presentation import Message, MessageReceiver

# External imports
from multidict import MultiDict

# Type-checking names
_MessageReceivers = Iterable[MessageReceiver]


# Commands, RPC-style

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


class MessageNotifier(object):
    """Mixin to send a message to registered receivers."""

    def __init__(self, message_receivers: Optional[_MessageReceivers]=None):
        """Initialize member variables."""
        self.message_receivers: List[MessageReceiver] = []
        if message_receivers:
            self.message_receivers = [receiver for receiver in message_receivers]

    async def notify_message_receivers(self, message: Message) -> None:
        """Pass the stored version to all registered version receivers.

        Does not wait for responses from any receivers.
        """
        for receiver in self.message_receivers:
            await receiver.on_message(message)


class CommandIssuer(MessageNotifier):
    """Mixin to send and wait for completion of a command to registered receivers."""

    def __init__(self, command_receivers: Optional[_MessageReceivers]=None):
        """Initialize member variables."""
        super().__init__(message_receivers=command_receivers)
        self.__issued_commands: Dict[str, Command] = {}

    def on_response(self, response_channel: str) -> None:
        """Handle a potential response for any issued commands."""
        for (command_channel, command) in self.__issued_commands.items():
            command.on_response(response_channel)

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
        await self.notify_message_receivers(command.message)
        await command.wait_task
        del self.__issued_commands[command.message.channel]
