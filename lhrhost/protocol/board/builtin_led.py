"""BuiltinLED channels of board protocol."""

# Standard imports
import logging
from abc import abstractmethod
from typing import Iterable, List, Optional

# Local package imports
from lhrhost.messaging.presentation import Message
from lhrhost.protocol import (
    ChannelHandlerTreeChildNode, ChannelHandlerTreeNode,
    Command, CommandIssuer
)
from lhrhost.util.interfaces import InterfaceClass
from lhrhost.util.printing import Printer

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# Receipt of BuiltinLED

class BuiltinLEDReceiver(object, metaclass=InterfaceClass):
    """Interface for a class which receives builtin_led events.

    This may include versions from self or from other sources.
    """

    @abstractmethod
    async def on_builtin_led(self, state: int) -> None:
        """Receive and handle a BuiltinLED response."""
        pass

    @abstractmethod
    async def on_builtin_led_blink(self, state: int) -> None:
        """Receive and handle a BuiltinLED/Blink response."""
        pass

    @abstractmethod
    async def on_builtin_led_blink_high_interval(self, interval: int) -> None:
        """Receive and handle a BuiltinLED/Blink/HighInterval response."""
        pass

    @abstractmethod
    async def on_builtin_led_blink_low_interval(self, interval: int) -> None:
        """Receive and handle a BuiltinLED/Blink/LowInterval response."""
        pass

    @abstractmethod
    async def on_builtin_led_blink_periods(self, periods: int) -> None:
        """Receive and handle a BuiltinLED/Blink/Periods response."""
        pass

    @abstractmethod
    async def on_builtin_led_blink_notify(self, state: int) -> None:
        """Receive and handle a BuiltinLED/Blink/Notify response."""
        pass


# Type-checking names
_BuiltinLEDReceivers = Iterable[BuiltinLEDReceiver]


# Printing

class BuiltinLEDPrinter(BuiltinLEDReceiver, Printer):
    """Simple class which prints received serialized messages."""

    async def on_builtin_led(self, state: int) -> None:
        """Receive and handle a BuiltinLED response."""
        self.print('Built-in LED: {}'.format(
            'HIGH' if state else 'LOW'
        ))

    async def on_builtin_led_blink(self, state: int) -> None:
        """Receive and handle a BuiltinLED/Blink response."""
        self.print('Built-in LED blink: {}'.format(
            'blinking' if state else 'constant'
        ))

    async def on_builtin_led_blink_high_interval(self, interval: int) -> None:
        """Receive and handle a BuiltinLED/Blink/HighInterval response."""
        self.print('Built-in LED blink high interval: {}'.format(interval))

    async def on_builtin_led_blink_low_interval(self, interval: int) -> None:
        """Receive and handle a BuiltinLED/Blink/LowInterval response."""
        self.print('Built-in LED blink low interval: {}'.format(interval))

    async def on_builtin_led_blink_periods(self, periods: int) -> None:
        """Receive and handle a BuiltinLED/Blink/Periods response."""
        self.print('Built-in LED blink periods: {}'.format(periods))

    async def on_builtin_led_blink_notify(self, state: int) -> None:
        """Receive and handle a BuiltinLED/Blink/Notify response."""
        self.print('Built-in LED blink notifications: {}'.format(
            'notifying' if state else 'not notifying'
        ))


class BuiltinLEDBlinkProtocol(ChannelHandlerTreeChildNode, CommandIssuer):
    """Blinks the built-in LED."""

    def __init__(self, *args, **kwargs):
        """Initialize member variables."""
        super().__init__(*args, **kwargs)
        self.command_receivers = self.parent.command_receivers
        self.builtin_led_receivers = self.parent.builtin_led_receivers

    async def notify_builtin_led_receivers(self, state: int) -> None:
        """Notify all receivers of received BuiltinLED/Blink response."""
        for receiver in self.builtin_led_receivers:
            await receiver.on_builtin_led_blink(state)

    async def notify_builtin_led_receivers_high_interval(self, interval: int) -> None:
        """Notify all receivers of received BuiltinLED/Blink/HighInterval response."""
        for receiver in self.builtin_led_receivers:
            await receiver.on_builtin_led_blink_high_interval(interval)

    async def notify_builtin_led_receivers_low_interval(self, interval: int) -> None:
        """Notify all receivers of received BuiltinLED/Blink/LowInterval response."""
        for receiver in self.builtin_led_receivers:
            await receiver.on_builtin_led_blink_low_interval(interval)

    async def notify_builtin_led_receivers_periods(self, periods: int) -> None:
        """Notify all receivers of received BuiltinLED/Blink/Periods response."""
        for receiver in self.builtin_led_receivers:
            await receiver.on_builtin_led_blink_periods(periods)

    async def notify_builtin_led_receivers_notify(self, state: int) -> None:
        """Notify all receivers of received BuiltinLED/Blink/Notify response."""
        for receiver in self.builtin_led_receivers:
            await receiver.on_builtin_led_blink_notify(state)

    # Commands

    async def request(self, state: Optional[int]=None):
        """Send a BuiltinLED/Blink request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path, state)
        await self.issue_command(Command(message))

    async def request_complete(self, periods: int):
        """Send a BuiltinLED/Blink request command to message receivers.

        Blink the built-in LED for a finite number of periods.
        """
        # TODO: validate periods
        message = Message(self.name_path, 1)
        wait_channels = [self.name_path, self.name_path, self.name_path + 'p']
        await self.request_periods(periods)
        logger.debug('Starting to blink the LED...')
        await self.issue_command(Command(message, wait_channels))
        logger.debug('Finished blinking the LED...')

    async def request_high_interval(self, interval: Optional[int]=None):
        """Send a BuiltinLED/Blink/HighInterval request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path + 'h', interval)
        await self.issue_command(Command(message))

    async def request_low_interval(self, interval: Optional[int]=None):
        """Send a BuiltinLED/Blink/LowInterval request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path + 'l', interval)
        await self.issue_command(Command(message))

    async def request_periods(self, periods: Optional[int]=None):
        """Send a BuiltinLED/Blink/Periods request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path + 'p', periods)
        await self.issue_command(Command(message))

    async def request_notify(self, state: Optional[int]=None):
        """Send a BuiltinLED/Blink/Notify request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path + 'n', state)
        await self.issue_command(Command(message))

    # Implement ChannelHandlerTreeNode

    @property
    def child_handlers(self):
        """Return a dict of handlers, keyed by channel paths below current path."""
        return {
            'h': self.on_received_message_high_interval,
            'l': self.on_received_message_low_interval,
            'p': self.on_received_message_periods,
            'n': self.on_received_message_notify,
        }

    async def on_received_message_high_interval(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_builtin_led_receivers_high_interval(message.payload)

    async def on_received_message_low_interval(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_builtin_led_receivers_low_interval(message.payload)

    async def on_received_message_periods(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_builtin_led_receivers_periods(message.payload)

    async def on_received_message_notify(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_builtin_led_receivers_notify(message.payload)

    async def on_any_message(self, message):
        """Handle any message whether or not it is recognized as by the node."""
        if message.payload is None:
            return
        self.on_response(message.channel)

    async def on_received_message(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the node."""
        if message.payload is None:
            return
        if message.channel == self.name_path:
            await self.notify_builtin_led_receivers(message.payload)


class BuiltinLEDProtocol(ChannelHandlerTreeNode, CommandIssuer):
    """Sets the built-in LED."""

    def __init__(
        self, builtin_led_receivers: Optional[_BuiltinLEDReceivers]=None, **kwargs
    ):
        """Initialize member variables."""
        super().__init__(**kwargs)
        self.builtin_led_receivers: List[BuiltinLEDReceiver] = []
        if builtin_led_receivers:
            self.builtin_led_receivers = [receiver for receiver in builtin_led_receivers]

        self.blink = BuiltinLEDBlinkProtocol(self, 'Blink', 'b', **kwargs)

    async def notify_builtin_led_receivers(self, state: int) -> None:
        """Notify all receivers of received BuiltinLED response."""
        for receiver in self.builtin_led_receivers:
            await receiver.on_builtin_led(state)

    # Commands

    async def request(self, state: Optional[int]=None):
        """Send a BuiltinLED request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path, state)
        await self.issue_command(Command(message))

    # Implement ChannelTreeNode

    @property
    def node_channel(self) -> str:
        """Return the channel of the node as a string."""
        return 'BuiltinLED'

    @property
    def node_name(self) -> str:
        """Return the channel name of the node as a string."""
        return 'l'

    @property
    def children(self):
        """Return a dict of the child ChannelTreeNodes keyed by prefixes."""
        return {
            self.blink.node_name: self.blink
        }

    # Implement MessageReceiver

    async def on_any_message(self, message):
        """Handle any message whether or not it is recognized as by the node."""
        if message.payload is None:
            return
        self.on_response(message.channel)

    async def on_received_message(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the node."""
        if message.payload is None:
            return
        # TODO: validate the channel name
        if message.channel == self.name_path:
            await self.notify_builtin_led_receivers(message.payload)
