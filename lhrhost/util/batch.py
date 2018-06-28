"""Support for batch execution."""

# Standard imports
import asyncio
import logging
try:
    import readline  # Import readline for better UX with input prompts
    readline
except ImportError:
    pass
from abc import abstractmethod

# Local package imports
from lhrhost.util.concurrency import Concurrent

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# Printing
OUTPUT_WIDTH = 6
OUTPUT_HEADER = (
    'Commands' + ('\t' * (OUTPUT_WIDTH - 1)) + 'Responses' + '\n' +
    ('-' * (12 * OUTPUT_WIDTH + 8))
)
OUTPUT_FOOTER = (
    ('-' * (12 * OUTPUT_WIDTH + 8))
)
RESPONSE_PREFIX = '\t' * OUTPUT_WIDTH


class BatchExecutionManager(Concurrent):
    """Abstract class to manage batch execution asynchronously.

    Creates an asynchronous coroutine which reads lines from stdin on a separate
    thread and handles them.
    """

    def __init__(self, ready_waiter=None):
        """Initialize member variables."""
        self._loop = asyncio.get_event_loop()
        # Batch execution
        self._ready_waiter = ready_waiter
        self._batch_execution_task = None

    # Implement Concurrent

    def start(self):
        """Start the associated asynchronous tasks."""
        self._start_batch_execution_task()

    def stop(self):
        """Stop the associated asynchronous tasks."""
        if self._batch_execution_task is not None:
            self._batch_execution_task.cancel()

    # Batch execution

    @abstractmethod
    def quit(self):
        """Quit after batch execution completes."""
        pass

    @abstractmethod
    async def on_execution_ready(self):
        """Take some action when the execution becomes possible."""
        pass

    async def _run_batch_execution(self):
        """Monitor the transport actor and restart it when it dies."""
        if callable(self._ready_waiter):
            await self._ready_waiter()
        logger.info('Ready for batch execution!')
        await self.on_execution_ready()
        self.quit()
        while True:
            await asyncio.sleep(1.0)

    def _start_batch_execution_task(self):
        if self._batch_execution_task is not None:
            self._batch_execution_task.cancel()
        self._batch_execution_task = self._loop.create_task(self._run_batch_execution())
