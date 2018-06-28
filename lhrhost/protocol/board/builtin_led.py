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
    async def on_builtin_led_blink_periods(self, state: int) -> None:
        """Receive and handle a BuiltinLED/Blink/Periods response."""
        pass

    @abstractmethod
    async def on_builtin_led_blink_notify(self, periods: int) -> None:
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

    async def notify_builtin_led_receivers(self, state: int) -> None:
        """Notify all receivers of received BuiltinLED response."""
        for receiver in self.__builtin_led_receivers:
            await receiver.on_builtin_led(state)

    async def notify_builtin_led_receivers_blink(self, state: int) -> None:
        """Notify all receivers of received BuiltinLED/Blink response."""
        for receiver in self.__builtin_led_receivers:
            await receiver.on_builtin_led_blink(state)

    async def notify_builtin_led_receivers_blink_high_interval(self, interval: int) -> None:
        """Notify all receivers of received BuiltinLED/Blink/HighInterval response."""
        for receiver in self.__builtin_led_receivers:
            await receiver.on_builtin_led_blink_high_interval(interval)

    async def notify_builtin_led_receivers_blink_low_interval(self, interval: int) -> None:
        """Notify all receivers of received BuiltinLED/Blink/LowInterval response."""
        for receiver in self.__builtin_led_receivers:
            await receiver.on_builtin_led_blink_low_interval(interval)

    async def notify_builtin_led_receivers_blink_notify(self, state: int) -> None:
        """Notify all receivers of received BuiltinLED/Blink/Notify response."""
        for receiver in self.__builtin_led_receivers:
            await receiver.on_builtin_led_blink_notify(state)

    # Commands

    async def request_builtin_led(self, state: Optional[int]=None):
        """Send a BuiltinLED request command to message receivers."""
        # TODO: validate the state
        message = Message('l', state)
        await self.issue_command(Command(message))

    async def request_builtin_led_blink(self, state: Optional[int]=None):
        """Send a BuiltinLED/Blink request command to message receivers."""
        # TODO: validate the state
        message = Message('lb', state)
        await self.issue_command(Command(message))

    async def request_complete_builtin_led_blink(self, periods: int):
        """Send a BuiltinLED/Blink request command to message receivers.

        Blink the built-in LED for a finite number of periods.
        """
        # TODO: validate periods
        message = Message('lb', 1)
        wait_channels = ['lb', 'lb', 'lbp']
        await self.request_builtin_led_blink_periods(periods)
        logger.debug('Starting to blink the LED...')
        await self.issue_command(Command(message, wait_channels))
        logger.debug('Finished blinking the LED...')

    async def request_builtin_led_blink_high_interval(self, interval: Optional[int]=None):
        """Send a BuiltinLED/Blink/HighInterval request command to message receivers."""
        # TODO: validate the state
        message = Message('lbh', interval)
        await self.issue_command(Command(message))

    async def request_builtin_led_blink_low_interval(self, interval: Optional[int]=None):
        """Send a BuiltinLED/Blink/LowInterval request command to message receivers."""
        # TODO: validate the state
        message = Message('lbl', interval)
        await self.issue_command(Command(message))

    async def request_builtin_led_blink_periods(self, periods: Optional[int]=None):
        """Send a BuiltinLED/Blink/Periods request command to message receivers."""
        # TODO: validate the state
        message = Message('lbp', periods)
        await self.issue_command(Command(message))

    async def request_builtin_led_blink_notify(self, state: Optional[int]=None):
        """Send a BuiltinLED/Blink/Notify request command to message receivers."""
        # TODO: validate the state
        message = Message('lbn', state)
        await self.issue_command(Command(message))

    # Implement MessageReceiver

    async def on_message(self, message: Message) -> None:
        """Handle received message.

        Only handles known BuiltinLED/* messages.
        """
        if message.payload is None:
            return
        # TODO: validate the channel name
        if message.channel == 'l':
            await self.notify_builtin_led_receivers(message.payload)
        elif message.channel == 'lb':
            await self.notify_builtin_led_receivers_blink(message.payload)
        elif message.channel == 'lbh':
            await self.notify_builtin_led_receivers_blink_high_interval(message.payload)
        elif message.channel == 'lbl':
            await self.notify_builtin_led_receivers_blink_low_interval(message.payload)
        elif message.channel == 'lbn':
            await self.notify_builtin_led_receivers_blink_notify(message.payload)
        self.on_response(message.channel)
