"""Support for command-line interfaces."""

# Standard imports
import asyncio
try:
    import readline  # Import readline for better UX with input prompts
except ImportError:
    pass
from abc import abstractmethod

# Local package imports
from lhrhost.util.concurrency import Concurrent


class ConsoleManager(Concurrent):
    """Abstract class to manage console input asynchronously.

    Creates an asynchronous coroutine which reads lines from stdin on a separate
    thread and handles them.
    """

    def __init__(self, executor):
        """Initialize member variables."""
        self.executor = executor
        self._loop = asyncio.get_event_loop()
        # Console prompt
        self._console_prompt_task = None

    # Implement Concurrent

    def start(self):
        """Start the associated asynchronous tasks."""
        self._start_console_prompt_task()

    def stop(self):
        """Stop the associated asynchronous tasks."""
        if self._console_prompt_task is not None:
            print('Cancelling...')
            self._console_prompt_task.cancel()

    # Console prompt

    def get_console_input(self):
        """Get a line of user input from stdin and return it, stripped at the ends."""
        try:
            return input().strip()
        except (EOFError, KeyboardInterrupt):
            pass
        return None

    @abstractmethod
    async def handle_console_input(self, input_line):
        """Take action based on the provided input.

        Raise KeyboardInterrupt when the input specifies that the console needs to
        stop running.
        """
        pass

    @abstractmethod
    def quit(self):
        """Handle a quit input provided by the user via the console prompt."""
        pass

    async def _loop_console_prompt(self):
        """Monitor the transport actor and restart it when it dies."""
        while True:
            input_line = await self._loop.run_in_executor(
                self.executor, self.get_console_input
            )
            try:
                await self.handle_console_input(input_line)
            except KeyboardInterrupt:
                self.quit()

    def _start_console_prompt_task(self):
        if self._console_prompt_task is not None:
            self._console_prompt_task.cancel()
        self._console_prompt_task = self._loop.create_task(self._loop_console_prompt())
