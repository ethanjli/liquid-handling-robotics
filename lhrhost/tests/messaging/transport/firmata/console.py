"""Exposes a command-line serial console to the peripheral."""
# Standard imports
import asyncio
import concurrent
import time

# Local package imports
from lhrhost.messaging.transport.firmata import TransportConnectionManager
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
    transport_manager = TransportConnectionManager(transport_kwargs=transport_kwargs)
    async with transport_manager.connection as transport:
        actor.transport = transport
        while True:
            await asyncio.sleep(60.0)


class Console:
    """Actor-based serial console."""

    def __init__(self, config):
        self.arbiter = arbiter(
            cfg=config, start=self.start, stopping=self.stop
        )
        self.message_printer = SerializedMessagePrinter()
        self.transport_actor = None
        self.transport_actor_task = None
        self.transport_actor_monitor_task = None
        self.console_prompt_task = None
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    def start(self, arbiter):
        self.start_transport_actor_task()
        self.start_transport_actor_monitor_task()
        self.start_console_prompt_task()

    def stop(self, arbiter):
        if self.transport_actor_task is not None:
            self.transport_actor_task.cancel()
        if self.console_prompt_task is not None:
            self.console_prompt_task.cancel()
        if self.transport_actor_monitor_task is not None:
            self.transport_actor_monitor_task.cancel()
        self.executor.shutdown()

    # Transport actor

    async def start_transport_actor(self):
        self.transport_actor = await spawn(
            name='transport', stopping=self.stop_transport_actor_task
        )
        print('Started transport actor!')
        # print(self.transport_actor.info_state)
        transport_kwargs = {
            'serialized_message_receivers': [self.message_printer]
        }
        await send(
            self.transport_actor, 'run', loop_transport,
            transport_kwargs=transport_kwargs
        )

    def start_transport_actor_task(self):
        loop = asyncio.get_event_loop()
        self.transport_actor_task = loop.create_task(self.start_transport_actor())

    def stop_transport_actor_task(self, actor):
        self.transport_actor_task.cancel()

    # Console input

    def start_console_prompt_task(self):
        loop = asyncio.get_event_loop()
        self.console_prompt_task = loop.create_task(self.loop_console_prompt())

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

    # Transport actor monitoring

    async def monitor_transport_actor(self):
        while True:
            if self.transport_actor is not None and not self.transport_actor.is_alive():
                print('Restarting transport actor...')
                self.start_transport_actor_task()
                await asyncio.sleep(1.0)
            await asyncio.sleep(1.0)

    def start_transport_actor_monitor_task(self):
        loop = asyncio.get_event_loop()
        self.transport_actor_monitor_task = loop.create_task(self.monitor_transport_actor())


if __name__ == '__main__':
    config = Config()
    config.parse_command_line()
    console = Console(config)
    console.arbiter.start()
