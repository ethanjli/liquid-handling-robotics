#!/usr/bin/python
"""Turns on an LED on for one second, then off for one second, repeatedly."""
import asyncio

from pymata_aio.constants import Constants
from pymata_aio.pymata3 import PyMata3

BOARD_LED = 13
board = PyMata3()

MESSAGE_SYSEX_COMMAND = 0x0F

establishedConnection = False


def send_handshake(board):
    """Start a serial connection."""
    print('Sending handshake')
    send_sysex(board, MESSAGE_SYSEX_COMMAND, [])


async def message_sysex_listener(sysex_data):
    """Handle a message sysex."""
    if len(sysex_data) == 2:
        print('Established connection!')
        global establishedConnection
        establishedConnection = True
        return
    print('Received message: "{}"'.format(''.join([chr(byte) for byte in sysex_data[1:-1]])))


def register_sysex_listener(board, command, callback):
    """Register a listener for a sysex command."""
    board.core.command_dictionary[command] = callback


def send_sysex(board, command, data):
    """Send a sysex command to the board."""
    task = asyncio.ensure_future(board.core._send_sysex(command, data))
    board.loop.run_until_complete(task)


def encode_message(message_string):
    """Build a message to send in a sysex command."""
    return [ord(char) for char in message_string]


def main_manual():
    """Blink with direct Firmata control."""
    board.set_pin_mode(BOARD_LED, Constants.OUTPUT)
    while True:
        print('LED On')
        board.digital_write(BOARD_LED, 1)
        board.sleep(1.0)
        print('LED Off')
        board.digital_write(BOARD_LED, 0)
        board.sleep(1.0)


def main_indirect():
    """Blink with indirect Firmata control."""
    global establishedConnection
    while not establishedConnection:
        send_handshake(board)
        board.sleep(1.0)
    message_template = '<l>({})'
    while True:
        print('LED On')
        send_sysex(board, MESSAGE_SYSEX_COMMAND, encode_message(message_template.format(1)))
        board.sleep(1.0)
        print('LED Off')
        send_sysex(board, MESSAGE_SYSEX_COMMAND, encode_message(message_template.format(0)))
        board.sleep(1.0)


if __name__ == '__main__':
    register_sysex_listener(board, MESSAGE_SYSEX_COMMAND, message_sysex_listener)
    try:
        # main_manual()
        main_indirect()
    except KeyboardInterrupt:
        print('Quitting!')
