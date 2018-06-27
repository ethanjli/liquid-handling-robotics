"""Turns on an LED on for one second, then off for one second, repeatedly."""
# Standard imports
import asyncio

# Local package imports
from lhrhost.messaging.transport import SerializedMessagePrinter
from lhrhost.messaging.transport.ascii import TransportConnectionManager


async def blink(transport):
    """Blink."""
    await transport.send_serialized_message('<lbn>({})'.format(1))
    await transport.send_serialized_message('<lb>({})'.format(1))
    while True:
        await asyncio.sleep(1.0)


async def main():
    """Blink with direct Firmata control."""
    transport_manager = TransportConnectionManager()
    while True:
        try:
            async with transport_manager.connection as transport:
                transport.serialized_message_receivers.append(SerializedMessagePrinter())
                await asyncio.gather(transport.task_receive_packets, blink(transport))
        except ConnectionAbortedError:
                print('Connection was lost! Please re-connect the device...')
        except ConnectionResetError:
            print('Connection was reset, starting over.')
        except KeyboardInterrupt:
            print('Quitting!')
            break


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print('Quitting!')
