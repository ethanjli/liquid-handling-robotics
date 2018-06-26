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
import lhrhost.messaging.transport.transport as transport
from lhrhost.messaging.transport.transport import (
    HANDSHAKE_RX_CHAR,
    PeripheralDisconnectedException,
    PeripheralResetException,
    SerializedMessageReceiver
)

# External imports
from serial import SerialException

import serial_asyncio

# Type-checking names
_Kwargs = Dict[str, Any]
_SerializedMessageReceivers = Iterable[SerializedMessageReceiver]

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
        handshake_message = str.encode(HANDSHAKE_RX_CHAR)
        message_line_suffix = str.encode(MESSAGE_LINE_SUFFIX)
        while True:
            try:
                line = await self.ser_reader.readuntil(message_line_suffix)
            except SerialException:
                raise PeripheralDisconnectedException
            if line.strip() == handshake_message:
                raise PeripheralResetException
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
        await self._establish_handshake()
        # Set up event handling
        self.transport = Transport(
            self._ser_reader, self._ser_writer, **self.transport_kwargs
        )
        self.transport.start_receiving_serialized_messages()
        return self.transport

    async def _establish_handshake(self) -> None:
        """Establish the transport-layer connection."""
        print('Please connect the device now...')
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
        print('Found the device! Initiating handshake for transport-layer connection...')
        self.transport = Transport(
            self._ser_reader, self._ser_writer, self.loop, **self.transport_kwargs
        )
        # Wait for handshake char (peripheral initiates handshake)
        message_line_suffix = str.encode(MESSAGE_LINE_SUFFIX)
        while self.transport is not None:
            try:
                line = await self._ser_reader.readuntil(message_line_suffix)
            except SerialException:
                raise PeripheralDisconnectedException
            if line.strip() == str.encode(HANDSHAKE_RX_CHAR):
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


class ASCIIMonitor():
    """Monitors an :class:`ASCIIConnection` for new lines in RX.

    Provides message loop to receive lines from the device and broadcast those
    received lines to listeners.
    Supports thread-based concurrency for receiving lines.
    Listens for lines and writes them to the connection.

    Args:
        connection: a valid ASCII connection for an open serial port.
        intercept_logging: whether to intercept logging messages and display
            them instead of passing them to listeners.

    Attributes:
        listeners (:obj:`list` of :class:`ASCIILineReceiver`): the line RX
            event listeners. Add and remove listeners to this attribute to
            update what listens for new lines in RX.
        intercept_logging (bool): whether to intercept logging messages and
            display them instead of passing them to listeners.

    """

    def __init__(self, connection, intercept_logging: bool=True):
        """Initialize member variables."""
        self._connection = connection
        self.intercept_logging = intercept_logging

        # Event-driven RX
        self.listeners = []
        self._monitoring = False

    # Monitoring

    def start_reading_lines(self) -> None:
        """Start the RX monitoring event loop and broadcast to listeners.

        Blocks the thread of the caller until a new line is received and
        :meth:`stop_reading_lines` is called or an exception (such as a
        :exc:`KeyboardInterrupt` or an interrupt from a listener) is
        encountered.
        """
        self._monitoring = True
        while self._monitoring:
            try:
                line = self._connection.read_line()
                if self.intercept_logging:
                    if line.startswith('E: '):
                        print('Error: {}'.format(line[3:]))
                        continue
                    elif line.startswith('W: '):
                        print('Warning: {}'.format(line[3:]))
                        continue
                if line == HANDSHAKE_RX_CHAR:
                    self.write_line('{}{}'.format(MESSAGE_LINE_PREFIX, MESSAGE_LINE_SUFFIX))
                    print('Connection was reset! Re-initiating serial handshake...')
                    for listener in self.listeners:
                        listener.on_connection_reset()
                else:
                    for listener in self.listeners:
                        listener.on_line(line)
            except KeyboardInterrupt:
                self._monitoring = False
            except Exception:
                self._monitoring = False
                raise

    def stop_reading_lines(self) -> None:
        """Make `start_reading_lines` quit after the current line.

        This needs to be called from a separate thread than the one running
        :meth:`start_reading_lines`.
        """
        self._monitoring = False

    @property
    def reading_lines(self) -> bool:
        """bool: Whether the RX monitoring event loop will continue."""
        return self._monitoring

    # Threading

    def start_thread(self) -> None:
        """Start monitoring RX in a new daemonic thread."""
        self._thread.start()

    def _stop_thread(self, timeout: int=200) -> None:
        """Stop monitoring RX.

        Currently non-functional because the thread will block on read_line.
        As a workaround, the thread is daemonic.
        """
        self.stop_reading_lines()
        self._thread.join(timeout=timeout / 1000)

    # Implement ASCIILineReceiver

    def on_line(self, line):
        """Handle a received line."""
        self._connection.write_line(line)
