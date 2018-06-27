"""Actors for the transport layer."""
# Standard imports
import asyncio

# External imports
import pulsar.api as ps


# Commands

@ps.command()
async def send_serialized_message(request, serialized_message):
    """Send a serialized message to an actor with a `transport` member."""
    await request.actor.transport.send_serialized_message(serialized_message)
    return serialized_message


# Actor Managers

class TransportManager(object):
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
        # Transport actor
        self._loop = asyncio.get_event_loop()
        self._actor = None
        self._actor_task = None
        self._transport_loop = transport_loop
        self._transport_connection_manager_kwargs = transport_connection_manager_kwargs
        # Transport actor monitor
        self._monitor_task = None
        self._monitor_poll_interval = monitor_poll_interval

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
        self._actor = await ps.spawn(
            name='transport', stopping=lambda actor: self._actor_task.cancel()
        )
        print('Started transport actor!')
        await ps.send(
            self._actor, 'run', self._transport_loop,
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
            if self._actor is not None and not self._actor.is_alive():
                print('Restarting transport actor...')
                self._start_actor_task()
            await asyncio.sleep(self._monitor_poll_interval)

    def _start_monitor_task(self):
        if self._monitor_task is not None:
            self._monitor_task.cancel()
        self._monitor_task = self._loop.create_task(self._monitor_transport_actor())
