"""Exposes a command-line serial console to the peripheral."""
# Standard imports
import asyncio
import concurrent
import sys

# Local package imports
from lhrhost.messaging.transport.ascii import TransportConnectionManager
from lhrhost.messaging.transport.transport import (
    PeripheralDisconnectedException,
    PeripheralResetException,
    SerializedMessagePrinter
)

# External imports
from pulsar.api import Config, arbiter, command, ensure_future, send, spawn


@command()
async def send_serialized_message(request, serialized_message):
    await request.actor.transport.send_serialized_message(serialized_message)
    return serialized_message


async def loop_transport(actor, transport_kwargs):
    """Run the transport layer.

    Attempts to restart the layer whenever the connection is broken.
    """
    transport_manager = TransportConnectionManager(
        port='/dev/ttyACM1', transport_kwargs=transport_kwargs
    )
    while True:
        try:
            async with transport_manager.connection as transport:
                actor.transport = transport
                actor.serialized_messages_queue = asyncio.Queue()
                await transport.task_receive_packets
        except PeripheralDisconnectedException:
                print('Connection was lost! Please re-connect the device...')
        except PeripheralResetException:
            print('Connection was reset, starting over.')
        except KeyboardInterrupt:
            print('Quitting!')
            break


class Console:
    """Actor-based serial console."""

    def __init__(self, config):
        self.arbiter = arbiter(cfg=config, start=self.start, stopping=self.stop)
        self.message_printer = SerializedMessagePrinter()
        self.transport_actor = None
        self.console_prompt_task = None
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    def start(self, arbiter):
        loop = asyncio.get_event_loop()
        ensure_future(self.start_transport_actor())
        self.console_prompt_task = loop.create_task(self.loop_console_prompt())

    def stop(self, arbiter):
        if self.console_prompt_task is not None:
            self.console_prompt_task.cancel()
        self.executor.shutdown()

    async def start_transport_actor(self):
        self.transport_actor = await spawn(name='transport')
        transport_kwargs = {
            'serialized_message_receivers': [self.message_printer]
        }
        await send(
            self.transport_actor, 'run', loop_transport,
            transport_kwargs=transport_kwargs
        )

    async def loop_console_prompt(self):
        """Run a command-line console prompt."""
        loop = asyncio.get_event_loop()
        while True:
            input_line = await loop.run_in_executor(None, self.get_console_input)
            await send(self.transport_actor, 'send_serialized_message', input_line)

    def get_console_input(self):
        input_line = input()
        if not input_line.strip():
            print('Quitting...')
            self.arbiter.stop()
        return input_line


if __name__ == '__main__':
    config = Config()
    config.parse_command_line()
    console = Console(config)
    console.arbiter.start()
