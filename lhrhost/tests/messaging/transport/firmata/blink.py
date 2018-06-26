"""Turns on an LED on for one second, then off for one second, repeatedly."""
# Standard imports
import asyncio

# Local package imports
from lhrhost.messaging.transport.firmata import TransportConnectionManager
from lhrhost.messaging.transport.transport import (
    PeripheralDisconnectedException,
    PeripheralResetException,
    SerializedMessagePrinter
)

from pymata_aio.constants import Constants

BOARD_LED = 13


async def blink(transport):
    """Blink."""
    await transport.board.set_pin_mode(BOARD_LED, Constants.OUTPUT)
    cycle = 0
    while True:
            await transport.board.digital_write(BOARD_LED, 1)
            await asyncio.sleep(1.0)
            await transport.board.digital_write(BOARD_LED, 0)
            await asyncio.sleep(1.0)
            await transport.send_serialized_message('<e>({})'.format(cycle))
            cycle += 1


async def main():
    """Blink with direct Firmata control."""
    transport_manager = TransportConnectionManager()
    while True:
        try:
            async with transport_manager.connection as transport:
                transport.serialized_message_receivers.append(SerializedMessagePrinter())
                await blink(transport)
        # Note: currently Pymata catches all exceptions (bad design) and quits
        # the entire program (bad design), so these exceptions aren't handled
        # here.
        except PeripheralDisconnectedException:
                print('Connection was lost! Please re-connect the device...')
        except PeripheralResetException:
            print('Connection was reset, starting over.')
        except KeyboardInterrupt:
            print('Quitting!')
            break



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
