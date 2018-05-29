#!/usr/bin/python
"""Turns on an LED on for one second, then off for one second, repeatedly."""
import asyncio

from pymata_aio.constants import Constants
from pymata_aio.pymata3 import PyMata3

BOARD_LED = 13
board = PyMata3()

MESSAGE_SYSEX_COMMAND = 0x0F


def send_sysex(board, command, data):
    """Send a sysex command to the board."""
    task = asyncio.ensure_future(board.core._send_sysex(command, data))
    board.loop.run_until_complete(task)


def build_message(message_string):
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
    message_template = '<l>({})'
    while True:
        print('LED On')
        send_sysex(board, MESSAGE_SYSEX_COMMAND, build_message(message_template.format(1)))
        board.sleep(1.0)
        print('LED Off')
        send_sysex(board, MESSAGE_SYSEX_COMMAND, build_message(message_template.format(0)))
        board.sleep(1.0)


def main_automatic():
    """Blink with indirect Firmata control."""
    send_sysex(board, MESSAGE_SYSEX_COMMAND, build_message('<l>(-1)'))  # LinearPositionControl's LED has a bug, this is a temporary workaround
    send_sysex(board, MESSAGE_SYSEX_COMMAND, build_message('<l>(-1)'))
    while True:
        pass


if __name__ == '__main__':
    # main_manual()
    # main_indirect()
    main_automatic()
