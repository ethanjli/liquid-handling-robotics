"""Exposes a command-line serial console to the peripheral."""
# Standard imports
import asyncio
import concurrent

# Local package imports
from lhrhost.messaging.transport import SerializedMessagePrinter
from lhrhost.messaging.transport.actors import TransportManager
from lhrhost.messaging.transport.ascii import transport_loop

# External imports
from pulsar.api import Config, arbiter, command, send


class Console:
    """Actor-based serial console."""

    def __init__(self, config):
        self.arbiter = arbiter(cfg=config, start=self.start, stopping=self.stop)
        self.message_printer = SerializedMessagePrinter()
        self.transport_monitor = TransportManager(
            self.arbiter, transport_loop,
            transport_kwargs={
                'serialized_message_receivers': [self.message_printer]
            }
        )
        self.console_prompt_task = None
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    def start(self, arbiter):
        self.transport_monitor.start()
        self.start_console_prompt_task()

    def stop(self, arbiter):
        self.transport_monitor.stop()
        if self.console_prompt_task is not None:
            self.console_prompt_task.cancel()
        self.executor.shutdown()

    # Console input

    def start_console_prompt_task(self):
        loop = asyncio.get_event_loop()
        self.console_prompt_task = loop.create_task(self.loop_console_prompt())

    async def loop_console_prompt(self):
        """Run a command-line console prompt."""
        loop = asyncio.get_event_loop()
        while True:
            input_line = await loop.run_in_executor(None, self.get_console_input)
            await send(self.transport_monitor._actor, 'send_serialized_message', input_line)

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
