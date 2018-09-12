"""Turns on an LED on for one second, then off for one second, repeatedly."""
# Standard imports
import asyncio
import logging

# External imports
from pymata_aio.pymata_core import PymataCore
from pymata_aio.constants import Constants

# Logging
logging.basicConfig(level=logging.INFO)

BOARD_LED = 13


async def main(board):
    """Blink with direct Firmata control."""
    await board.set_pin_mode(BOARD_LED, Constants.OUTPUT)
    while True:
        await board.digital_write(BOARD_LED, 1)
        await asyncio.sleep(1.0)
        await board.digital_write(BOARD_LED, 0)
        await asyncio.sleep(1.0)
        # Note: currently Pymata catches all exceptions (bad design) and quits
        # the entire program (bad design), so exceptions aren't handled here.


if __name__ == '__main__':
    board = PymataCore()
    board.start()
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(board))
    except KeyboardInterrupt:
        logging.info('Quitting!')
