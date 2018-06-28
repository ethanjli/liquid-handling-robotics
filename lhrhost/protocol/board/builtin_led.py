"""BuiltinLED channels of board protocol."""

# Standard imports
import logging
from abc import abstractmethod
from typing import Iterable, List, Optional

# Local package imports
from lhrhost.messaging.presentation import Message, MessageReceiver
from lhrhost.protocol import Command, CommandIssuer
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
    def on_builtin_led(self, state: int) -> None:
        """Receive and handle a BuiltinLED response."""
        pass

    @abstractmethod
    def on_builtin_led_blink(self, state: int) -> None:
        """Receive and handle a BuiltinLED/Blink response."""
        pass

    @abstractmethod
    def on_builtin_led_blink_high_interval(self, interval: int) -> None:
        """Receive and handle a BuiltinLED/Blink/HighInterval response."""
        pass

    @abstractmethod
    def on_builtin_led_blink_low_interval(self, interval: int) -> None:
        """Receive and handle a BuiltinLED/Blink/LowInterval response."""
        pass

    @abstractmethod
    def on_builtin_led_blink_periods(self, state: int) -> None:
        """Receive and handle a BuiltinLED/Blink/Periods response."""
        pass

    @abstractmethod
    def on_builtin_led_blink_notify(self, periods: int) -> None:
        """Receive and handle a BuiltinLED/Blink/Notify response."""
        pass


# Type-checking names
_BuiltinLEDReceivers = Iterable[BuiltinLEDReceiver]


# Printing

class BuiltinLEDPrinter(BuiltinLEDReceiver, Printer):
    """Simple class which prints received serialized messages."""

    def on_builtin_led(self, state: int) -> None:
        """Receive and handle a BuiltinLED response."""
        self.print('Built-in LED: {}'.format(
            'HIGH' if state else 'LOW'
        ))

    def on_builtin_led_blink(self, state: int) -> None:
        """Receive and handle a BuiltinLED/Blink response."""
        self.print('Built-in LED blink: {}'.format(
            'blinking' if state else 'constant'
        ))

    def on_builtin_led_blink_high_interval(self, interval: int) -> None:
        """Receive and handle a BuiltinLED/Blink/HighInterval response."""
        self.print('Built-in LED blink high interval: {}'.format(interval))

    def on_builtin_led_blink_low_interval(self, interval: int) -> None:
        """Receive and handle a BuiltinLED/Blink/LowInterval response."""
        self.print('Built-in LED blink low interval: {}'.format(interval))

    def on_builtin_led_blink_periods(self, periods: int) -> None:
        """Receive and handle a BuiltinLED/Blink/Periods response."""
        self.print('Built-in LED blink periods: {}'.format(periods))

    def on_builtin_led_blink_notify(self, state: int) -> None:
        """Receive and handle a BuiltinLED/Blink/Notify response."""
        self.print('Built-in LED blink notifications: {}'.format(
            'notifying' if state else 'not notifying'
        ))


class BuiltinLEDProtocol(MessageReceiver, CommandIssuer):
    """Determines and prints protocol version."""

    def __init__(
        self, builtin_led_receivers: Optional[_BuiltinLEDReceivers]=None, **kwargs
    ):
        """Initialize member variables."""
        super().__init__(**kwargs)
        self.__builtin_led_receivers: List[BuiltinLEDReceiver] = []
        if builtin_led_receivers:
            self.__builtin_led_receivers = [receiver for receiver in builtin_led_receivers]

    def notify_builtin_led_receivers(self, state: int) -> None:
        """Notify all receivers of received BuiltinLED response."""
        for receiver in self.__builtin_led_receivers:
            receiver.on_builtin_led(state)

    def notify_builtin_led_receivers_blink(self, state: int) -> None:
        """Notify all receivers of received BuiltinLED/Blink response."""
        for receiver in self.__builtin_led_receivers:
            receiver.on_builtin_led_blink(state)

    def notify_builtin_led_receivers_blink_high_interval(self, interval: int) -> None:
        """Notify all receivers of received BuiltinLED/Blink/HighInterval response."""
        for receiver in self.__builtin_led_receivers:
            receiver.on_builtin_led_blink_high_interval(interval)

    def notify_builtin_led_receivers_blink_low_interval(self, interval: int) -> None:
        """Notify all receivers of received BuiltinLED/Blink/LowInterval response."""
        for receiver in self.__builtin_led_receivers:
            receiver.on_builtin_led_blink_low_interval(interval)

    def notify_builtin_led_receivers_blink_notify(self, state: int) -> None:
        """Notify all receivers of received BuiltinLED/Blink/Notify response."""
        for receiver in self.__builtin_led_receivers:
            receiver.on_builtin_led_blink_notify(state)

    # Commands

    async def request_builtin_led(self, state: Optional[int]=None):
        """Send a BuiltinLED request command to message receivers."""
        # TODO: validate the state
        await self.notify_message_receivers(Message('l', state))

    async def request_wait_builtin_led(self, state: Optional[int]=None):
        """Send a BuiltinLED request command to message receivers."""
        # TODO: validate the state
        await self.issue_command(Command(Message('l', state), ['l']))

    async def request_builtin_led_blink(self, state: Optional[int]=None):
        """Send a BuiltinLED/Blink request command to message receivers."""
        # TODO: validate the state
        await self.notify_message_receivers(Message('lb', state))

    async def request_wait_builtin_led_blink(self, state: Optional[int]=None):
        """Send a BuiltinLED/Blink request command to message receivers."""
        # TODO: validate the state
        await self.issue_command(Command(Message('lb', state), ['lb']))

    async def request_complete_builtin_led_blink(self, periods: int):
        """Send a BuiltinLED/Blink request command to message receivers.

        Blink the built-in LED for a finite number of periods.
        """
        # TODO: validate periods
        await self.request_wait_builtin_led_blink_periods(periods)
        await self.issue_command(Command(Message('lb', 1), ['lb', 'lb', 'lbp']))

    async def request_builtin_led_blink_high_interval(self, interval: Optional[int]=None):
        """Send a BuiltinLED/Blink/HighInterval request command to message receivers."""
        # TODO: validate the state
        await self.notify_message_receivers(Message('lbh', interval))

    async def request_wait_builtin_led_blink_high_interval(self, interval: Optional[int]=None):
        """Send a BuiltinLED/Blink/HighInterval request command to message receivers."""
        # TODO: validate the state
        await self.issue_command(Command(Message('lbh', interval), ['lbh']))

    async def request_builtin_led_blink_low_interval(self, interval: Optional[int]=None):
        """Send a BuiltinLED/Blink/LowInterval request command to message receivers."""
        # TODO: validate the state
        await self.notify_message_receivers(Message('lbl', interval))

    async def request_wait_builtin_led_blink_low_interval(self, interval: Optional[int]=None):
        """Send a BuiltinLED/Blink/LowInterval request command to message receivers."""
        # TODO: validate the state
        await self.issue_command(Command(Message('lbl', interval), ['lbl']))

    async def request_builtin_led_blink_periods(self, periods: Optional[int]=None):
        """Send a BuiltinLED/Blink/Periods request command to message receivers."""
        # TODO: validate the state
        await self.notify_message_receivers(Message('lbp', periods))

    async def request_wait_builtin_led_blink_periods(self, periods: Optional[int]=None):
        """Send a BuiltinLED/Blink/Periods request command to message receivers."""
        # TODO: validate the state
        await self.issue_command(Command(Message('lbp', periods), ['lbp']))

    async def request_builtin_led_blink_notify(self, state: Optional[int]=None):
        """Send a BuiltinLED/Blink/Notify request command to message receivers."""
        # TODO: validate the state
        await self.notify_message_receivers(Message('lbn', state))

    async def request_wait_builtin_led_blink_notify(self, state: Optional[int]=None):
        """Send a BuiltinLED/Blink/Notify request command to message receivers."""
        # TODO: validate the state
        await self.issue_command(Command(Message('lbn', state), ['lbn']))

    # Implement DeserializedMessageReceiver

    async def on_message(self, message: Message) -> None:
        """Handle received message.

        Only handles known BuiltinLED/* messages.
        """
        if message.payload is None:
            return
        # TODO: validate the channel name
        if message.channel == 'l':
            self.notify_builtin_led_receivers(message.payload)
        elif message.channel == 'lb':
            self.notify_builtin_led_receivers_blink(message.payload)
        elif message.channel == 'lbh':
            self.notify_builtin_led_receivers_blink_high_interval(message.payload)
        elif message.channel == 'lbl':
            self.notify_builtin_led_receivers_blink_low_interval(message.payload)
        elif message.channel == 'lbn':
            self.notify_builtin_led_receivers_blink_notify(message.payload)
        self.on_response(message.channel)
