#!/usr/bin/python
"""Turns on an LED on for one second, then off for one second, repeatedly."""

from pymata_aio.constants import Constants
from pymata_aio.pymata3 import PyMata3

BOARD_LED = 13
board = PyMata3()


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


if __name__ == '__main__':
    main_manual()
