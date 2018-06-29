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


class BlinkHighIntervalProtocol(ProtocolHandlerNode):
    """Notifies on the Built-in LED blinker's HIGH interval."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('HighInterval', 'h', **kwargs)
        self.response_receivers = self.parent.response_receivers

    # Commands

    async def request(self, interval: Optional[int]=None):
        """Send a BuiltinLED/Blink/HighInterval request command to message receivers."""
        # TODO: validate the interval
        message = Message(self.name_path, interval)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_builtin_led_blink_high_interval


class BlinkLowIntervalProtocol(ProtocolHandlerNode):
    """Notifies on the Built-in LED blinker's LOW interval."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('LowInterval', 'l', **kwargs)
        self.response_receivers = self.parent.response_receivers

    # Commands

    async def request(self, interval: Optional[int]=None):
        """Send a BuiltinLED/Blink/LowInterval request command to message receivers."""
        # TODO: validate the interval
        message = Message(self.name_path, interval)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_builtin_led_blink_low_interval


class BlinkPeriodsProtocol(ProtocolHandlerNode):
    """Notifies on the Built-in LED blinker's LOW interval."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('Periods', 'p', **kwargs)
        self.response_receivers = self.parent.response_receivers

    # Commands

    async def request(self, periods: Optional[int]=None):
        """Send a BuiltinLED/Blink/Periods request command to message receivers."""
        # TODO: validate the periods
        message = Message(self.name_path, periods)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_builtin_led_blink_periods


class BlinkNotifyProtocol(ProtocolHandlerNode):
    """Notifies on the Built-in LED blinker's LOW interval."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('Notify', 'n', **kwargs)
        self.response_receivers = self.parent.response_receivers

    # Commands

    async def request(self, periods: Optional[int]=None):
        """Send a BuiltinLED/Blink/Notify request command to message receivers."""
        # TODO: validate the periods
        message = Message(self.name_path, periods)
        await self.issue_command(Command(message))

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_builtin_led_blink_notify


class BlinkProtocol(ProtocolHandlerNode):
    """Blinks the built-in LED."""

    def __init__(self, **kwargs):
        """Initialize member variables."""
        super().__init__('Blink', 'b', **kwargs)
        self.response_receivers = self.parent.response_receivers

        self.high_interval = BlinkHighIntervalProtocol(parent=self)
        self.low_interval = BlinkLowIntervalProtocol(parent=self)
        self.periods = BlinkPeriodsProtocol(parent=self)
        self.notify = BlinkNotifyProtocol(parent=self)

    # Implement ProtocolHandlerNode

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_builtin_led_blink

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
        await self.periods.request(periods)
        logger.debug('Starting to blink the LED...')
        await self.issue_command(Command(message, wait_channels))
        logger.debug('Finished blinking the LED...')

    # Implement ProtocolHandlerNode

    @property
    def children_list(self):
        """Return a list of child nodes."""
        return [self.high_interval, self.low_interval, self.periods, self.notify]


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

        self.blink = BlinkProtocol(parent=self, **kwargs)

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

    def get_response_notifier(self, receiver):
        """Return the response receiver's method for receiving a response."""
        return receiver.on_builtin_led
