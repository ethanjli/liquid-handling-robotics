"""Transport layer interfaces.

This module provides a shared interface for implementations of transport layers
in the host-peripheral messaging protocol.
"""

# Standard imports
from abc import abstractmethod
from typing import Any, Dict, Iterable, List, Optional

from async_generator import asynccontextmanager

# Local package imports
from lhrhost.util.interfaces import InterfaceClass

# Type-checking names
_Kwargs = Dict[str, Any]

# Protocol parameters
HANDSHAKE_RX_CHAR = '~'


# Receipt of serialized messages

class SerializedMessageReceiver(object, metaclass=InterfaceClass):
    """Interface for a class which receives serialized messages.

    This may include serialized messages from self or from other sources.
    """

    @abstractmethod
    def on_serialized_message(self, serialized_message: str) -> None:
        """Receive and handle a serialized message."""
        pass


# Type-checking names
_SerializedMessageReceivers = Iterable[SerializedMessageReceiver]


class SerializedMessagePrinter(SerializedMessageReceiver):
    """Simple class which prints received serialized messages."""

    def on_serialized_message(self, serialized_message: str) -> None:
        """Receive and handle a serialized message."""
        print(serialized_message)


# Interfaces for transport-layer implementations

class Transport(SerializedMessageReceiver, metaclass=InterfaceClass):
    """Abstract class for a transport layer with an established connection.

    Note that receipt of messages from the peripheral is only partially specified;
    the Transport and TransportConnectionManager must together do whatever is
    necessary for :meth:`on_serialized_message` to be called with every serialized
    message received.
    """

    def __init__(
        self,
        serialized_message_receivers: Optional[_SerializedMessageReceivers]=None
    ):
        """Initialize member variables."""
        self.__serialized_message_receivers: List[SerializedMessageReceiver] = []
        if serialized_message_receivers:
            self.__serialized_message_receivers = [
                receiver for receiver in serialized_message_receivers
            ]

    @abstractmethod
    async def close(self) -> None:
        """Close the transport-layer connection to the device.

        Blocks until the connection is closed.
        """
        pass

    @abstractmethod
    async def send_serialized_message(self, serialized_message: str) -> None:
        """Send the serialized message to the peripheral.

        A serialized message is typically provided by the presentation layer.
        """
        pass

    @abstractmethod
    def start_receiving_serialized_messages(self) -> None:
        """Start endlessly receiving and handling message data from the connection.

        Receiving of data should be asynchronous, so this function is non-blocking.
        """
        pass

    @property
    def serialized_message_receivers(self) -> _SerializedMessageReceivers:
        """Return an iterable of objects to forward received serialized messages to."""
        return self.__serialized_message_receivers

    # Implement SerializedMessageReceiver

    def on_serialized_message(self, serialized_message: str) -> None:
        """Receive and handle a serialized message.

        Simply forwards the received message to receivers in
        :meth:`serialized_message_receivers`.
        """
        for receiver in self.serialized_message_receivers:
            receiver.on_serialized_message(serialized_message)


class TransportConnectionManager(object, metaclass=InterfaceClass):
    """Abstract class for a transport-layer connection establisher."""

    def __init__(self, transport_kwargs: Optional[_Kwargs]= None):
        """Initialize member variables."""
        self.transport_kwargs: Optional[_Kwargs] = (
            transport_kwargs if transport_kwargs is not None else {}
        )
        self.transport: Optional[Transport] = None

    @abstractmethod
    async def open(self) -> Transport:
        """Establish and return a transport-layer connection to the device.

        Establishes a connection session with a mutual handshake specified by
        the transport-layer protocol. Once the connection is established,
        messages can be sent over the transport layer.
        """
        pass

    async def close(self) -> None:
        """Close the associated transport-layer connection, if it is open."""
        if self.transport is not None:
            await self.transport.close()
            self.transport = None

    @property
    @asynccontextmanager
    async def connection(self) -> Transport:
        """Return a Transport connection to the device."""
        self.transport = await self.open()
        try:
            yield self.transport
        except Exception as e:
            raise e
        finally:
            await self.close()

    async def reset(self) -> None:
        """Reset and close the Transport connection associated with the device."""
        if self.transport is not None:
            await self.close()
        async with self.connection:
            pass


class PeripheralDisconnectedException(Exception):
    """Exception raised by a Transport when the peripheral is disconnected.

    This occurs if, for example, the physical or data link layer connection is lost.
    """

    pass


class PeripheralResetException(Exception):
    """Exception raised by a Transport when the peripheral resets.

    This occurs if, for example, the peripheral resets without the host detecting
    loss of the physical or data link layer connection.
    """

    pass
