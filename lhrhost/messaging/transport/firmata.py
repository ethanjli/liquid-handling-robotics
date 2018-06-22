#!/usr/bin/python
"""Turns on an LED on for one second, then off for one second, repeatedly."""
import asyncio

from pymata_aio.constants import Constants
from pymata_aio.pymata3 import PyMata3

BOARD_LED = 13
MESSAGE_SYSEX_COMMAND = 0x0F

class Transport(object):
    """Firmata-based transport layer."""
    def __init__(self):
        self.board = PyMata3()
        self.establishedConnection = False

        self._register_sysex_listener(MESSAGE_SYSEX_COMMAND, self._on_sysex_message)

    def establish_connection(self, handshake_interval=1.0):
        """Start and finish a connection handshake with the board."""
        while not self.establishedConnection:
            self._send_handshake()
            self.board.sleep(handshake_interval)

    def send_message(self, message_string):
        """Send a message string to the board."""
        self._send_sysex(MESSAGE_SYSEX_COMMAND, self.encode_message(message_string))

    def encode_message(self, message_string):
        """Build a message to send in a sysex command."""
        return [ord(char) for char in message_string]

    def _send_handshake(self):
        """Start a serial connection."""
        print('Sending handshake...')
        self._send_sysex(MESSAGE_SYSEX_COMMAND, [])

    def _send_sysex(self, sysex_command, data):
        """Send a sysex command to the board."""
        task = asyncio.ensure_future(self.board.core._send_sysex(sysex_command, data))
        self.board.loop.run_until_complete(task)

    async def _on_sysex_message(self, sysex_data):
        """Handle a message sysex."""
        if len(sysex_data) == 2:
            print('Established connection!')
            self.establishedConnection = True
            return
        print('Received message: "{}"'.format(''.join([chr(byte) for byte in sysex_data[1:-1]])))

    def _register_sysex_listener(self, sysex_command, sysex_listener):
        """Register a listener for a sysex command."""
        self.board.core.command_dictionary[sysex_command] = sysex_listener


def main_manual(transport):
    """Blink with direct Firmata control."""
    transport.board.set_pin_mode(BOARD_LED, Constants.OUTPUT)
    while True:
        print('LED On')
        transport.board.digital_write(BOARD_LED, 1)
        transport.board.sleep(1.0)
        print('LED Off')
        transport.board.digital_write(BOARD_LED, 0)
        transport.board.sleep(1.0)


def main_indirect(transport):
    """Blink with indirect Firmata control."""
    transport.establish_connection()
    message_template = '<l>({})'
    while True:
        print('LED On')
        transport.send_message(message_template.format(1))
        transport.board.sleep(1.0)
        print('LED Off')
        transport.send_message(message_template.format(0))
        transport.board.sleep(1.0)


if __name__ == '__main__':
    transport = Transport()
    try:
        # main_manual(transport)
        main_indirect(transport)
    except KeyboardInterrupt:
        print('Quitting!')
