"""BuiltinLED channels of board protocol."""

# Standard imports
import logging
from abc import abstractmethod
from typing import Iterable, List, Optional

# Local package imports
from lhrhost.messaging.presentation import Message
from lhrhost.protocol import Command, ProtocolHandlerNode
from lhrhost.util.interfaces import InterfaceClass
from lhrhost.util.printing import Printer

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# Receipt of BuiltinLED

class Receiver(object, metaclass=InterfaceClass):
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
_Receivers = Iterable[Receiver]


# Printing

class Printer(Receiver, Printer):
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


class BuiltinLEDBlinkProtocol(ProtocolHandlerNode):
    """Blinks the built-in LED."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('Blink', 'b', **kwargs)
        self.response_receivers = self.parent.response_receivers

    async def notify_response_receivers(self, state: int) -> None:
        """Notify all receivers of received BuiltinLED/Blink response."""
        for receiver in self.response_receivers:
            await receiver.on_builtin_led_blink(state)

    async def notify_response_receivers_high_interval(self, interval: int) -> None:
        """Notify all receivers of received BuiltinLED/Blink/HighInterval response."""
        for receiver in self.response_receivers:
            await receiver.on_builtin_led_blink_high_interval(interval)

    async def notify_response_receivers_low_interval(self, interval: int) -> None:
        """Notify all receivers of received BuiltinLED/Blink/LowInterval response."""
        for receiver in self.response_receivers:
            await receiver.on_builtin_led_blink_low_interval(interval)

    async def notify_response_receivers_periods(self, periods: int) -> None:
        """Notify all receivers of received BuiltinLED/Blink/Periods response."""
        for receiver in self.response_receivers:
            await receiver.on_builtin_led_blink_periods(periods)

    async def notify_response_receivers_notify(self, state: int) -> None:
        """Notify all receivers of received BuiltinLED/Blink/Notify response."""
        for receiver in self.response_receivers:
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
        await self.notify_response_receivers_high_interval(message.payload)

    async def on_received_message_low_interval(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_response_receivers_low_interval(message.payload)

    async def on_received_message_periods(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_response_receivers_periods(message.payload)

    async def on_received_message_notify(self, channel_name_remainder, message):
        """Handle a message recognized as being handled by the child handler."""
        await self.notify_response_receivers_notify(message.payload)


class Protocol(ProtocolHandlerNode):
    """Sets the built-in LED."""

    def __init__(
        self, response_receivers: Optional[_Receivers]=None, **kwargs
    ):
        """Initialize member variables."""
        super().__init__('BuiltinLED', 'l', **kwargs)
        self.response_receivers: List[Receiver] = []
        if response_receivers:
            self.response_receivers = [receiver for receiver in response_receivers]

        self.blink = BuiltinLEDBlinkProtocol(parent=self, **kwargs)

    # Commands

    async def request(self, state: Optional[int]=None):
        """Send a BuiltinLED request command to message receivers."""
        # TODO: validate the state
        message = Message(self.name_path, state)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    @property
    def children_list(self):
        """Return a list of child nodes."""
        return [self.blink]

    async def notify_response_receivers(self, state: int) -> None:
        """Notify all receivers of received BuiltinLED response."""
        for receiver in self.response_receivers:
            await receiver.on_builtin_led(state)
