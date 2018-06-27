"""Firmata-based transport layer implementation."""

# Standard imports
import asyncio
import logging
from typing import Any, Dict, Iterable, List, Optional

# Local package imports
import lhrhost.messaging.transport as transport

# External imports
from pymata_aio.pymata_core import PymataCore

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Type-checking names
_Kwargs = Dict[str, Any]
_SerializedMessageReceivers = Iterable[transport.SerializedMessageReceiver]

# Protocol parameters
MESSAGE_SYSEX_COMMAND = 0x0F


# Transport-layer implementation

def encode_message(message_string: str) -> List[int]:
    """Build a message to send in a sysex command."""
    return [ord(char) for char in message_string]


def decode_message(sysex_data: List[int]) -> str:
    """Decode a message from sysex command data."""
    return ''.join(chr(byte) for byte in sysex_data[1:-1])


def message_empty(sysex_data: List[int]) -> bool:
    """Return whether the sysex data is an empty message packet."""
    return len(sysex_data) == 2


class Transport(transport.Transport):
    """Firmata-based transport layer with an established connection."""

    def __init__(self, board: PymataCore, **kwargs):
        """Initialize member variables."""
        super().__init__(**kwargs)
        self.board = board

    def register_message_listener(self, sysex_listener) -> None:
        """Register a listener for a sysex command."""
        self.board.command_dictionary[MESSAGE_SYSEX_COMMAND] = sysex_listener

    async def on_sysex_message(self, sysex_data: List[int]) -> None:
        """Handle a message sysex."""
        decoded = decode_message(sysex_data)
        if message_empty(sysex_data) or decoded == transport.HANDSHAKE_RX_CHAR:
            raise ConnectionResetError
        await self.on_serialized_message(decoded)

    # Implement transport.Transport

    def start_receiving_serialized_messages(self) -> None:
        """Start endlessly receiving and handling message data from the connection.

        Receiving of data is asynchronous, and the associated event loop must be run.
        """
        self.register_message_listener(self.on_sysex_message)

    def close(self) -> None:
        """Close the transport-layer connection to the device.

        Blocks until the connection is closed.
        """
        self.board.shutdown()

    async def send_serialized_message(self, serialized_message: str) -> None:
        """Send the serialized message to the peripheral.

        Blocks until the line is fully written.
        A serialized message is typically provided by the presentation layer.
        """
        await self.board._send_sysex(MESSAGE_SYSEX_COMMAND, encode_message(serialized_message))


class TransportConnectionManager(transport.TransportConnectionManager):
    """Firmata-based transport connection manager."""

    def __init__(
        self, handshake_attempt_interval: float=0.2,
        board_kwargs: Optional[_Kwargs]=None,
        transport_kwargs: Optional[_Kwargs]=None
    ):
        """Initialize member variables."""
        super().__init__(transport_kwargs=transport_kwargs)
        # Firmata board
        self._board_kwargs: Optional[dict] = (
            board_kwargs if board_kwargs is not None else {}
        )
        self._board: Optional[PymataCore] = None
        # Mutual handshake parameters
        self._handshake_attempt_interval: float = handshake_attempt_interval
        # State
        self._handshake_started: bool = False
        self._connected: bool = False

    # Implement transport.TransportConnectionManager

    async def open(self) -> Transport:
        """Establish and return a transport-layer connection to the device.

        Establishes a connection session with a mutual handshake specified by
        the transport-layer protocol. Once the connection is established,
        messages can be sent over the transport layer.

        Blocks until the connection is established.
        """
        # Connect board
        logger.info('Please plug in the device now...')
        self._board = PymataCore(**self._board_kwargs)
        await self._board.start_aio()
        logger.debug('Established datalink-layer connection!')
        self._handshake_started = False
        self._connected = False
        # Establish mutual handshake
        self.transport = Transport(self._board, **self.transport_kwargs)
        self.transport.register_message_listener(self._on_sysex_message)
        logger.debug('Initiating handshake for transport-layer connection...')
        while self.transport is not None and not self._connected:
            if self._handshake_started:
                await self.transport.send_serialized_message('')
            await asyncio.sleep(self._handshake_attempt_interval)
        # Set up event handling
        self.transport.start_receiving_serialized_messages()
        logger.info('Established transport-layer connection!')
        return self.transport

    async def _on_sysex_message(self, sysex_data) -> None:
        """Handle a message sysex before transport-layer connection is established."""
        if (
            (not self._handshake_started) and
            (decode_message(sysex_data) == transport.HANDSHAKE_RX_CHAR)
        ):
            logger.debug('Handshake started!')
            self._handshake_started = True
        elif self._handshake_started and message_empty(sysex_data):
            logger.debug('Completed handshake!')
            self._connected = True
        elif self._connected and self.transport is not None:
            await self.transport.on_sysex_message(sysex_data)

    async def close(self) -> None:
        """Close the associated transport-layer connection, if it is open."""
        await super().close()
        self._handshake_started = False
        self._connected = False


# Actors

async def transport_loop(actor, on_connection=None, on_disconnection=None, **kwargs):
    """Run the transport layer as an asynchronous actor loop.

    Dies whenever the connection is broken, due to the design of Pymata.
    """
    logger.debug('Started transport loop!')
    transport_connection_manager = TransportConnectionManager(**kwargs)
    async with transport_connection_manager.connection as transport_connection:
        actor.transport = transport_connection
        if callable(on_connection):
            await on_connection(
                actor, transport_connection_manager, transport_connection
            )
        while True:  # only stops when Pymata forces a sys.exit
            await asyncio.sleep(1.0)
    if callable(on_disconnection):
        await on_disconnection(actor, transport_connection_manager)
