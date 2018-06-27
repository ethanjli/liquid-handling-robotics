"""Actors for the transport layer."""

# Standard imports
import asyncio
import logging

# Local package imports
from lhrhost.util import cli
from lhrhost.util.concurrency import Concurrent

# External imports
import pulsar.api as ps

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# Commands

@ps.command()
async def send_serialized_message(request, serialized_message):
    """Send a serialized message to an actor with a `transport` member."""
    try:
        await request.actor.transport.send_serialized_message(serialized_message)
    except AttributeError:
        logger.warning((
            'Error: serialized message "{}" not sent to "{}" actor, which is '
            'not yet able to receive such messages'
        ).format(serialized_message, request.actor.name))
    return serialized_message


@ps.command()
async def transport_connected(request):
    """Notify an actor that the transport layer connection has been established."""
    request.actor.transport_manager.on_transport_connected()


@ps.command()
async def transport_disconnected(request):
    """Notify an actor that the transport layer connection has been lost."""
    request.actor.transport_manager.on_transport_disconnected()


# Actor Managers

async def on_transport_connected(actor, transport_connection_manager, transport_connection):
    """Update a transport layer actor to reflect that it has obtained a connection."""
    await ps.send('arbiter', 'transport_connected')


async def on_transport_disconnected(actor, transport_connection_manager):
    """Update a transport layer actor to reflect that it lost its connection."""
    await ps.send('arbiter', 'transport_disconnected')


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
        self.arbiter.transport_manager = self
        self._loop = asyncio.get_event_loop()
        # Transport actor
        self.actor = None
        self._actor_task = None
        self._transport_loop = transport_loop
        self._transport_connection_manager_kwargs = transport_connection_manager_kwargs
        # Transport actor monitor
        self._monitor_task = None
        self._monitor_poll_interval = monitor_poll_interval
        # Synchronization
        self._transport_connected = asyncio.Event()
        self._transport_disconnected = asyncio.Event()
        self._transport_disconnected.set()

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
            name='transport_layer', stopping=self._stop_actor_task
        )
        logger.debug('Started transport actor!')
        await ps.send(
            self.actor, 'run', self._transport_loop,
            on_transport_connected, on_transport_disconnected,
            **self._transport_connection_manager_kwargs
        )

    def _start_actor_task(self):
        """Create a task to start the actor."""
        if self._actor_task is not None:
            self._actor_task.cancel()
        self._actor_task = self._loop.create_task(self._start_transport_actor())

    def _stop_actor_task(self, actor):
        self._actor_task.cancel()
        self.on_transport_disconnected()

    # Transport actor monitor

    async def _monitor_transport_actor(self):
        """Monitor the transport actor and restart it when it dies."""
        while True:
            if self.actor is not None and not self.actor.is_alive():
                logger.warning('Restarting transport actor...')
                self._start_actor_task()
            await asyncio.sleep(self._monitor_poll_interval)

    def _start_monitor_task(self):
        if self._monitor_task is not None:
            self._monitor_task.cancel()
        self._monitor_task = self._loop.create_task(self._monitor_transport_actor())

    # Synchronization

    def on_transport_connected(self):
        """Set event flags to notify waiters of connection."""
        if not self._transport_connected.is_set():
            logger.info('Transport connected!')
        else:
            logger.warning('Transport was already connected!')
        self._transport_connected.set()
        self._transport_disconnected.clear()

    def on_transport_disconnected(self):
        """Set event flags to notify waiters of disconnection."""
        logger.info('Transport disconnected!')
        self._transport_connected.clear()
        self._transport_disconnected.set()

    async def wait_transport_connected(self):
        """Block until connection."""
        await self._transport_connected.wait()

    async def wait_transport_disconnected(self):
        """Block until disconnection."""
        await self._transport_connected.wait()


class ConsoleManager(cli.ConsoleManager):
    """Class to pass console input as send_serialized_message actor commands.

    Creates an asynchronous coroutine which reads lines from stdin on a separate
    thread and handles them by sending them to actors.

    This can be used to send lines on stdin as message packets to the actor for
    a transport-layer connection to a peripheral, for example.

    We don't put this in a separate actor - that fails because stdin
    on a separate actor only receives EOF for some reason.
    """

    def __init__(self, arbiter, get_command_targets, console_header='', **kwargs):
        """Initialize member variables."""
        super().__init__(**kwargs)
        self.arbiter = arbiter
        self._loop = asyncio.get_event_loop()
        # Console prompt
        self._console_prompt_task = None
        self._console_header = console_header
        self.__get_command_targets = get_command_targets

    def forward_input_line(self, input_line, command_target):
        """Forward the serialized command message to a target."""
        try:
            ps.send(command_target, 'send_serialized_message', input_line)
        except BrokenPipeError:
            pass

    # Implement ConsoleManager

    def quit(self):
        """Monitor the transport actor and restart it when it dies."""
        logger.info('Quitting...')
        self.arbiter.stop()

    def on_console_ready(self):
        """Take some action when the console is ready."""
        if self._console_header:
            print(self._console_header)

    async def handle_console_input(self, input_line):
        """Take action based on the provided input.

        Raise KeyboardInterrupt when the input specifies that the console needs to
        stop running. Empty input is a signal to quit.
        """
        if not input_line:
            raise KeyboardInterrupt
        asyncio.wait([
            self.forward_input_line(input_line, command_target)
            for command_target in self.__get_command_targets()
        ])
