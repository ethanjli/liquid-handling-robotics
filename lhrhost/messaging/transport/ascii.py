#!/usr/bin/env python3
"""Device communication over USB serial.

This module implements event-driven communication protocols with devices
over USB serial connections. The protocol should be chosen to match the
protocol selected for the device board.
"""

# Standard imports
import asyncio
from asyncio import StreamReader, StreamWriter
from typing import Any, Dict, Iterable, Optional

# Local package imports
import lhrhost.messaging.transport as transport

# External imports
from serial import SerialException

import serial_asyncio

# Type-checking names
_Kwargs = Dict[str, Any]
_SerializedMessageReceivers = Iterable[transport.SerializedMessageReceiver]

# Protocol parameters
MESSAGE_LINE_PREFIX = ''
MESSAGE_LINE_SUFFIX = '\n'


# Transport-layer implementation

class Transport(transport.Transport):
    """ASCII-based transport layer with an established connection.

    Provides functionality to transmit strings and lines to the device, and to
    receive lines from the device.
    """

    def __init__(self, ser_reader: StreamReader, ser_writer: StreamWriter, loop=None, **kwargs):
        """Initialize member variables."""
        super().__init__(**kwargs)
        self.ser_reader: StreamReader = ser_reader
        self.ser_writer: StreamWriter = ser_writer
        self.loop: asyncio.AbstractEventLoop = (
            loop if loop is not None else asyncio.get_event_loop()
        )
        self.task_receive_packets = None

    # Implement transport.Transport

    def start_receiving_serialized_messages(self) -> None:
        """Start endlessly receiving and handling message data from the connection.

        Receiving of data is asynchronous, and the associated event loop must be run.
        """
        self.task_receive_packets = self.loop.create_task(self._receive_packets())

    async def _receive_packets(self) -> None:
        """Endlessly receive serialized messages from the connection and handle them."""
        handshake_message = str.encode(transport.HANDSHAKE_RX_CHAR)
        message_line_suffix = str.encode(MESSAGE_LINE_SUFFIX)
        while True:
            try:
                line = await self.ser_reader.readuntil(message_line_suffix)
            except SerialException:
                raise ConnectionAbortedError
            if line.strip() == handshake_message:
                raise ConnectionResetError
            self.on_serialized_message(line.strip().decode())

    async def close(self) -> None:
        """Close the transport-layer connection to the device.

        Blocks until the connection is closed.
        """
        if self.task_receive_packets is not None:
            self.task_receive_packets.cancel()
            self.task_receive_packets = None
        self.ser_reader = None
        self.ser_writer.close()
        self.ser_writer = None

    async def send_serialized_message(self, serialized_message: str) -> None:
        """Send the serialized message to the peripheral.

        Blocks until the line is fully written.

        Args:
            line: a line which can be passed into a string format.
            end: a string or character to add to the end of the line. Default:
                newline character.
        """
        self.ser_writer.write(('{}{}{}'.format(
            MESSAGE_LINE_PREFIX, serialized_message, MESSAGE_LINE_SUFFIX
        )).encode('utf-8'))


class TransportConnectionManager(transport.TransportConnectionManager):
    """ASCII-based transport connection manager.

    Provides functionality to transmit strings and lines to the device, and to
    receive lines from the device.

    Args:
        port: if `ser` is `None`, specifies which serial port to open.
            Otherwise, it's ignored. Default: `/dev/ttyACM0`.
        baudrate: if `ser` is `None`, the serial connection baud rate.
            Otherwise, it's ignored. Default: 115200.
        handshake_attempt_interval: interval in milliseconds to wait after
            receiving a non-handshake character before trying again.
            Default: 200 ms.

    Attributes:
        handshake_attempt_interval (int): interval in milliseconds to wait after
            receiving a non-handshake character before trying again.

    """

    def __init__(
        self, handshake_attempt_interval: float=0.2,
        port: str='/dev/ttyACM0', baudrate: int=115200,
        transport_kwargs: Optional[_Kwargs]=None
    ):
        """Initialize member variables."""
        super().__init__(transport_kwargs=transport_kwargs)
        # Serial port
        self._port: str = port
        self._baudrate: int = baudrate
        self._ser_reader: Optional[StreamReader] = None
        self._ser_writer: Optional[StreamWriter] = None
        # Mutual handshake parameters
        self.handshake_attempt_interval: float = handshake_attempt_interval
        # State
        self.loop = asyncio.get_event_loop()

    # Implement transport.TransportConnectionManager

    async def open(self) -> Transport:
        """Establish and return a transport-layer connection to the device.

        Establishes a connection session with a mutual handshake specified by
        the transport-layer protocol. Once the connection is established,
        messages can be sent over the transport layer.

        Blocks until the connection is established.
        """
        # Connect the board and establish mutual handshake
        await self._connect_datalink()
        self.transport = Transport(
            self._ser_reader, self._ser_writer, self.loop, **self.transport_kwargs
        )
        await self._establish_handshake()
        # Set up event handling
        self.transport = Transport(
            self._ser_reader, self._ser_writer, **self.transport_kwargs
        )
        self.transport.start_receiving_serialized_messages()
        print('Established transport-layer connection!')
        return self.transport

    async def _connect_datalink(self) -> None:
        """Establish the datalink-layer connection."""
        print('Please plug in the device now...')
        while True:
            try:
                (
                    self._ser_reader, self._ser_writer
                ) = await serial_asyncio.open_serial_connection(
                    url=self._port, baudrate=self._baudrate, loop=self.loop
                )
                break
            except SerialException:
                await asyncio.sleep(self.handshake_attempt_interval)
        print('Established datalink-layer connection!')

    async def _establish_handshake(self) -> None:
        """Establish the transport-layer connection."""
        print('Initiating handshake for transport-layer connection...')
        # Wait for handshake char (peripheral initiates handshake)
        message_line_suffix = str.encode(MESSAGE_LINE_SUFFIX)
        while self.transport is not None:
            try:
                line = await self._ser_reader.readuntil(message_line_suffix)
            except SerialException:
                raise ConnectionAbortedError
            if line.strip().decode() == transport.HANDSHAKE_RX_CHAR:
                break
            await asyncio.sleep(self.handshake_attempt_interval)
        # Respond with empty message (host acknowledges handshake)
        await self.transport.send_serialized_message('')
        # Wait for empty response (peripheral confirms handshake established)
        while self.transport is not None:
            line = await self._ser_reader.readuntil(message_line_suffix)
            if not line.strip():
                break
        print('Completed handshake!')


# Actors

async def transport_loop(actor, on_connection=None, on_disconnection=None, **kwargs):
    """Run the transport layer as an asynchonous actor loop.

    Attempts to restart the layer whenever the connection is broken.
    """
    transport_connection_manager = TransportConnectionManager(**kwargs)
    while True:
        try:
            async with transport_connection_manager.connection as transport_connection:
                actor.transport = transport_connection
                if callable(on_connection):
                    await on_connection(
                        actor, transport_connection_manager, transport_connection
                    )
                await transport_connection.task_receive_packets  # only stops upon exception
        except ConnectionAbortedError:
            print('Connection to device lost! Please reconnect the device...')
        except ConnectionResetError:
            print('Connection was reset! Reconnecting...')
        except KeyboardInterrupt:
            print('Quitting...')
            break
        finally:
            if callable(on_disconnection):
                await on_disconnection(actor, transport_connection_manager)
