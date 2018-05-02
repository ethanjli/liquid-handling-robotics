#!/usr/bin/env python3
"""Device communication over USB serial.

This module implements event-driven communication protocols with devices
over USB serial connections. The protocol should be chosen to match the
protocol selected for the device board.
"""

# Standard imports
import time
import threading
from abc import abstractmethod
from typing import Any, Iterable

# External imports
import serial

# Local package imports
from lhrhost.util.interfaces import InterfaceClass

class Connection(object, metaclass=InterfaceClass):
    """Interface for a connection with a serial device."""

    @property
    @abstractmethod
    def port(self) -> str:
        """str: The port of the serial connection."""
        pass

    @property
    @abstractmethod
    def baudrate(self) -> int:
        """str: The port of the serial connection."""
        pass

    @abstractmethod
    def _connect(self) -> None:
        """Establish a serial connection to the device.

        Blocks until the serial connection is established.
        """
        pass

    @abstractmethod
    def _wait_for_handshake(self) -> None:
        """Establish a serial connection handshake with the device.

        Blocks until the handshake is established.
        """
        pass

    def open(self) -> None:
        """Connect and establish a handshake with the device.

        Blocks until the handshake is established.
        """
        self._connect()
        self._wait_for_handshake()

    @abstractmethod
    def close(self) -> None:
        """Close the connection to the device.

        Blocks until the connection is closed.
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Force the connected device to reset.

        Blocks until the connection is reset.
        """
        pass

# ASCII Connections

class ASCIIConnection(Connection):
    """ASCII-based connection with a serial device.

    Provides functionality to transmit strings and lines to the device, and to
    receive lines from the device.

    Args:
        ser (:obj:`serial.Serial`, optional): an already-opened serial port.
            Default: `None`, so port and baudrate will be used to create a new
            serial port.
        port: if `ser` is `None`, specifies which serial port to open.
            Otherwise, it's ignored. Default: `/dev/ttyACM0`.
        baudrate: if `ser` is `None`, the serial connection baud rate.
            Otherwise, it's ignored. Default: 115200.
        connect_poll_interval: interval in milliseconds to wait after a failed
            attempt to open the serial port before trying again.
            Default: 200 ms.
        handshake_poll_interval: interval in milliseconds to wait after
            receiving a non-handshake character before trying again.
            Default: 200 ms.
        handshake_rx_char: the handshake character to recognize in RX before
            sending `handshake_tx_char` to establish a handshake. Default: '~'.
        handshake_tx_char: the handshake character to send in TX to establish
            a handshake. Default: newline character.

    Attributes:
        connect_poll_interval (int): interval in milliseconds to wait after a
            failed attempt to open the serial port before trying again.
        handshake_poll_interval (int): interval in milliseconds to wait after
            receiving a non-handshake character before trying again.
        handshake_rx_char (str): the handshake character to recognize in RX
            before sending `handshake_tx_char` to establish a handshake.
        handshake_tx_char (str): the handshake character to send in TX to
            establish a handshake.
    """
    def __init__(
        self, ser: serial.Serial=None,
        port: str='/dev/ttyACM0', baudrate: int=115200,
        connect_poll_interval: int=200, handshake_poll_interval: int=200,
        handshake_rx_char: str='~', handshake_tx_char: str='\n'
    ):
        # Serial port
        if ser is not None:
            port = ser.port
            baudrate = ser.baudrate
        self._port: str = port
        self._baudrate: int = baudrate
        self._ser: serial.Serial = ser

        # Serial connection parameters
        self.connect_poll_interval: int = connect_poll_interval
        self.handshake_poll_interval: int = handshake_poll_interval
        self.handshake_rx_char: str = handshake_rx_char
        self.handshake_tx_char: str = handshake_tx_char

    # Implement Connection

    @property
    def port(self) -> str:
        """str: The port of the serial connection."""
        return self._port

    @property
    def baudrate(self) -> int:
        """str: The port of the serial connection."""
        return self._baudrate

    def _connect(self) -> None:
        print('Please connect the device now...')
        while True:
            try:
                self.ser = serial.Serial(self._port, self._baudrate)
                break
            except serial.serialutil.SerialException:
                time.sleep(self.connect_poll_interval / 1000)
        print('Connected!')

    def _wait_for_handshake(self) -> None:
        while True:
            char = self.read_line()
            if char == self.handshake_rx_char:
                self.write_line(self.handshake_tx_char)
                print('Completed handshake!')
                return
            time.sleep(self.handshake_poll_interval / 1000)

    def close(self) -> None:
        self.ser.close()

    def reset(self) -> None:
        if self.ser.isOpen():
            self.ser.close()
        self.ser.open()
        self.ser.close()

    # RX/TX

    def read_line(self) -> str:
        """Reads a full line from the device.

        Blocks until a newline is received.

        Returns:
            The complete line that was just received, stripped of newlines.
        """
        # TODO: add nonblocking implementation of read_line
        return str(self.ser.readline(), 'ascii').rstrip()

    def write_line(self, line: Any, end: str='\n') -> None:
        """Writes a string or line to the device.

        Blocks until the line is fully written.

        Args:
            line: a line which can be passed into a string format.
            end: a string or character to add to the end of the line. Default:
                newline character.
        """
        self.ser.write(('{}{}'.format(line, end)).encode('utf-8'))

class ASCIILineReceiver(object, metaclass=InterfaceClass):
    """Interface for event listeners for an :class:`ASCIIMonitor`."""

    @abstractmethod
    def on_line(self, line: str) -> None:
        """Event handler for a new line received over RX.

        Args:
            line: an ASCII line received over RX
        """
        pass

    def on_connection_reset(self) -> None:
        """Event handler for a reset of the serial connection.
        """
        pass

class ASCIIMonitor(ASCIILineReceiver):
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
    def __init__(self, connection: ASCIIConnection, intercept_logging: bool=True):
        self._connection = connection
        self.intercept_logging = intercept_logging

        # Event-driven RX
        self.listeners = []
        self._monitoring = False

        # Threading
        self._thread = threading.Thread(
            name=self.__class__, target=self.start_reading_lines, daemon=True
        )

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
                if line == self._connection.handshake_rx_char:
                    self._connection.write_line(self._connection.handshake_tx_char)
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
        self._connection.write_line(line)

class ASCIIConsole(ASCIILineReceiver):
    """ASCII serial command-line console for an :class:`ASCIIConnection`.

    Provides mostly-equivalent functionality to Arduino IDE's Serial Monitor.

    Args:
        connection (:obj:`ASCIIConnection`): a valid and open ASCII connection
            for a serial port.
        add_as_listener: whether to add the ASCII console as a RX listener to
            the monitor.
    """
    def __init__(self, connection: ASCIIConnection):
        self._connection = connection

    def start_input_loop(self) -> None:
        """Monitor the command-line for messages to send as TX.

        Input on the command-line is sent to the device by TX, while lines
        from the device on RX are printed to the command-line. TX monitoring
        blocks on the calling thread and must be interrupted with a
        :exc:`KeyboardInterrupt`.
        """
        try:
            while True:
                self._connection.write_line(input())
        except KeyboardInterrupt:
            return

    # Implement ASCIILineReceiver

    def on_line(self, line: str) -> None:
        print(line)

def main() -> None:
    """Runs a command-line serial console for a device over USB."""
    connection = ASCIIConnection()
    monitor = ASCIIMonitor(connection)
    console = ASCIIConsole(connection)

    monitor.listeners.append(console)

    connection.open()
    monitor.start_thread()
    console.start_input_loop()
    connection.reset()

if __name__ == '__main__':
    main()

