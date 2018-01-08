""" Arduino communication over USB serial.

This module implements event-driven communication protocols with Arduino boards
over USB serial connections. The protocol should be chosen to match the
protocol selected for the Arduino board.
"""

import time
import threading
from typing import Any, Iterable

import serial

class ASCIIConnection(object):
    """ASCII-based serial connection with an Arduino board.

    Provides interfaces to transmit strings and lines to the Arduino,
    and to receive lines from the Arduino.

    Attributes:
        connect_poll_interval (int): interval in milliseconds to wait after a
            failed attempt to open the serial port before trying again.
        handshake_poll_interval (int): interval in milliseconds to wait after
            receiving a non-handshake character before trying again.
        handshake_rx_char (str): the handshake character to recognize in RX
            before sending `handshake_tx_char` to establish a handshake.
        handshake_tx_char (str): the handshake character to send in TX to
            establish a handshake.

    Args:
        ser: an already-opened serial port. Default: `None`, so port and
            baudrate will be used to create a new serial port.
        port: if `ser` is None, specifies which serial port to open. Default:
            `/dev/ttyACM0`, which is the default on Linux.
        baudrate: the serial connection baud rate. Default: 115200.
        connect_poll_interval: interval in milliseconds to wait after a failed
            attempt to open the serial port before trying again.
            Default: 200 ms.
        handshake_poll_interval: interval in milliseconds to wait after
            receiving a non-handshake character before trying again.
            Default: 200 ms.
        handshake_rx_char: the handshake character to recognize in RX before
            sending `handshake_tx_char` to establish a handshake. Default: '~'.
        handshake_tx_char: the handshake character to send in TX to establish
            a handshake. Default: '\n'.
    """
    def __init__(
        self, ser: serial.Serial=None,
        port: str='/dev/ttyACM0', baudrate: int=115200,
        connect_poll_interval: int=200, handshake_poll_interval: int=200,
        handshake_rx_char: str='~', handshake_tx_char: str='\n'
    ) -> None:
        # Serial port
        if ser is not None:
            port = ser.port
            baudrate = ser.baudrate
        self._port = port
        self._baudrate = baudrate
        self._ser = ser

        # Serial connection parameters
        self.connect_poll_interval = connect_poll_interval
        self.handshake_poll_interval = handshake_poll_interval
        self.handshake_rx_char = '~'
        self.handshake_tx_char = '\n'

    # Serial properties

    @property
    def port(self) -> str:
        """The port of the serial connection."""
        return self._port

    @property
    def baudrate(self) -> int:
        """The baud rate of the serial connection."""
        return self._baudrate

    # Setup

    def connect(self) -> None:
        """Establish a serial connection to the Arduino board.

        Blocks until the serial connection is established.
        """
        print('Please connect the device now...')
        while True:
            try:
                self.ser = serial.Serial(self._port, self._baudrate)
                break
            except serial.serialutil.SerialException:
                time.sleep(self.connect_poll_interval / 1000)
        print('Connected!')

    def wait_for_handshake(self) -> None:
        """Establish a serial connection handshake with the Arduino board.

        Blocks until the handshake is established.
        """
        while True:
            char = self.ser.read().decode('utf-8')
            if char == self.handshake_rx_char:
                self.write_string(self.handshake_tx_char)
                print('Completed handshake!')
                return
            time.sleep(self.handshake_poll_interval / 1000)

    def setup(self) -> None:
        """Connect and establish a handshake with an Arduino board.

        Blocks until the handshake is established.
        """
        self.connect()
        self.wait_for_handshake()

    # Teardown

    def close(self) -> None:
        """Close the connection to the connected Arduino.

        Blocks until the connection is closed.
        """
        self.ser.close()

    def reset(self) -> None:
        """Force the connected Arduino to reset.

        Blocks until the Serial connection is reset.
        """
        if self.ser.isOpen():
            self.ser.close()
        self.ser.open()
        self.ser.close()

    # RX/TX

    def read_line(self) -> str:
        """Reads a full line from the Arduino.

        Blocks until a newline is received.

        Returns:
            The complete line that was just received, stripped of newlines.
        """
        # TODO: add nonblocking implementation of read_line
        return str(self.ser.readline(), 'ascii').rstrip()

    def write_line(self, line: Any, end: str='\n') -> None:
        """Writes a string or line to the Arduino.

        Blocks until the line is fully written.

        Args:
            line: a line which can be passed into a string format.
            end: a string or character to add to the end of the line. Default:
                `\n`.
        """
        self.ser.write(('{}{}'.format(line, end)).encode('utf-8'))

class ASCIIRXListener(object):
    """Interface for event listeners for an :class:`ASCIIMonitor`."""

    def on_read_line(self, line: str) -> None:
        """Event handler for a new line received over RX."""
        pass

class ASCIIMonitor(object):
    """Monitors an ASCIIConnection for new lines in RX.

    Provides event-driven interface to receive lines from the Arduino and
    broadcast those received lines to listeners.
    Supports thread-based concurrency for receiving lines.

    Attributes:
        listeners (:obj:`list` of :class:`ASCIIRXListener`): the line RX event
            listeners. Add and remove listeners to this attribute to update
            what listens for new lines in RX.

    Args:
        connection: a valid ASCII connection for an open serial port.
        listeners: any listeners immediately register.
    """
    def __init__(self, connection: ASCIIConnection,
                 listeners: Iterable[ASCIIRXListener]=[]) -> None:
        self._connection = connection

        # Event-driven RX
        self.listeners = [listener for listener in listeners]
        self._monitoring = False

        # Threading
        self._thread = threading.Thread(
            name=self.__name__, target=self.start_read_lines, daemon=True
        )

    # Monitoring

    def start_read_lines(self) -> None:
        """Start the RX monitoring event loop and broadcast to listeners.

        Blocks the thread of the caller until a new line is received and
        `stop_read_lines` is called or an exception (such as a
        `KeyboardInterrupt` or an interrupt from a listener) is encountered.
        """
        self._monitoring = True
        try:
            while self.monitoring:
                line = self._connection.read_line()
                for listener in self.listeners:
                    listener.on_read_line(line)
        except Exception:
            self._monitoring = False
            raise

    def stop_read_lines(self) -> None:
        """Make `start_read_lines` quit after the current line.

        This needs to be called from a separate thread than the one running
        start_read_lines.
        """
        self._monitoring = False

    @property
    def reading_lines(self) -> bool:
        """Whether the RX monitoring event loop will continue monitoring RX."""
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
        self.stop_read_lines()
        self._thread.join(timeout=timeout / 1000)

class ASCIIConsole(object):
    """ASCII serial command-line console for an :class:`ASCIIConnection`.

    Provides mostly-equivalent functionality to Arduino IDE's Serial Monitor.

    Args:
        connection: a valid ASCII connection for an open serial port.
            Default: `None`, so a new ASCII connection will be instantiated
            with default parameters.
        monitor: a valid ASCII monitor. This is expected to use the same ASCII
            connection as provided by connection. If connection is `None`, this
            will be ignored and a new ASCII monitor will be instantiated.
            Default: `None`, so a new ASCII monitor will be instantiated with
            default init parameters for the ASCII connection specified by
            connection.
        add_as_listener: whether to add the ASCII console as a RX listener to
            the monitor.
    """
    def __init__(self, connection: ASCIIConnection=None,
                 monitor: ASCIIMonitor=None,
                 add_as_listener: bool=True) -> None:
        if connection is None:
            self._connection = ASCIIConnection()
        else:
            self._connection = connection
        if connection is None or monitor is None:
            self._monitor = ASCIIMonitor(self._connection)
        else:
            self._monitor = monitor
        if add_as_listener:
            self._monitor.listeners.append(self)

    def setup(self) -> None:
        """Set up the ASCII connection."""
        self._arduino.setup()

    def start(self) -> None:
        """Monitor the connection for RX and the command-line for TX.

        Input on the command-line is sent to the Arduino by TX, while lines
        from the Arduino on RX are printed to the command-line. RX monitoring
        occurs on a separate thread, while TX monitoring blocks on the calling
        thread and must be interrupted with a :exc:`KeyboardInterrupt`.
        """
        self._monitor.start_thread()
        try:
            while True:
                self._arduino.write_line(input())
        except KeyboardInterrupt:
            pass
        self.teardown()

    def on_read_line(self, line: str) -> None:
        """Print the received line."""
        print(line)

    def teardown(self) -> None:
        """Reset the ASCII connection."""
        print()
        print('Quitting...')
        self._arduino.reset()

def main():
    console = Console()
    console.setup()
    console.start()

if __name__ == '__main__':
    main()

