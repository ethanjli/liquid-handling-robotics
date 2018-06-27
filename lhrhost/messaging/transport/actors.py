"""Actors for the transport layer."""

# Standard imports
import asyncio

# Local package imports
from lhrhost.util import cli
from lhrhost.util.concurrency import Concurrent

# External imports
import pulsar.api as ps


# Commands

@ps.command()
async def send_serialized_message(request, serialized_message):
    """Send a serialized message to an actor with a `transport` member."""
    await request.actor.transport.send_serialized_message(serialized_message)
    return serialized_message


# Actor Managers

class TransportManager(Concurrent):
    """Manages actor for a transport-layer asynchronous actor loop.

    Creates an actor which runs the transport layer in a separate process, and
    an asynchronous monitor in the parent thread which restarts the actor if it dies.
    """

    def __init__(
            self, arbiter, transport_loop, monitor_poll_interval=2.0,
            **transport_connection_manager_kwargs
    ):
        """Initialize member variables."""
        self.arbiter = arbiter
        self._loop = asyncio.get_event_loop()
        # Transport actor
        self.actor = None
        self._actor_task = None
        self._transport_loop = transport_loop
        self._transport_connection_manager_kwargs = transport_connection_manager_kwargs
        # Transport actor monitor
        self._monitor_task = None
        self._monitor_poll_interval = monitor_poll_interval

    # Implement Concurrent

    def start(self):
        """Start the associated asynchronous tasks."""
        self._start_actor_task()
        self._start_monitor_task()

    def stop(self):
        """Stop the associated asynchronous tasks."""
        if self._actor_task is not None:
            self._actor_task.cancel()
        if self._monitor_task is not None:
            self._monitor_task.cancel()

    # Transport actor

    async def _start_transport_actor(self):
        """Start the actor."""
        self.actor = await ps.spawn(
            name='transport', stopping=lambda actor: self._actor_task.cancel()
        )
        self.actor.transport = None
        print('Started transport actor!')
        await ps.send(
            self.actor, 'run', self._transport_loop,
            **self._transport_connection_manager_kwargs
        )

    def _start_actor_task(self):
        """Create a task to start the actor."""
        if self._actor_task is not None:
            self._actor_task.cancel()
        self._actor_task = self._loop.create_task(self._start_transport_actor())

    # Transport actor monitor

    async def _monitor_transport_actor(self):
        """Monitor the transport actor and restart it when it dies."""
        while True:
            if self.actor is not None and not self.actor.is_alive():
                print('Restarting transport actor...')
                self._start_actor_task()
            await asyncio.sleep(self._monitor_poll_interval)

    def _start_monitor_task(self):
        if self._monitor_task is not None:
            self._monitor_task.cancel()
        self._monitor_task = self._loop.create_task(self._monitor_transport_actor())


class ConsoleManager(cli.ConsoleManager):
    """Class to pass console input as send_serialized_message actor commands.

    Creates an asynchronous coroutine which reads lines from stdin on a separate
    thread and handles them by sending them to actors.

    This can be used to send lines on stdin as message packets to the actor for
    a transport-layer connection to a peripheral, for example.
    """

    def __init__(self, arbiter, executor, get_command_targets):
        """Initialize member variables."""
        super().__init__(executor)
        self.arbiter = arbiter
        self._loop = asyncio.get_event_loop()
        # Console prompt
        self._console_prompt_task = None
        self.__get_command_targets = get_command_targets

    # Implement ConsoleManager

    def quit(self):
        """Monitor the transport actor and restart it when it dies."""
        print('Quitting...')
        self.arbiter.stop()

    async def handle_console_input(self, input_line):
        """Take action based on the provided input.

        Raise KeyboardInterrupt when the input specifies that the console needs to
        stop running. Empty input is a signal to quit.
        """
        if not input_line:
            raise KeyboardInterrupt
        asyncio.wait([
            ps.send(command_target, 'send_serialized_message', input_line)
            for command_target in self.__get_command_targets()
        ])
