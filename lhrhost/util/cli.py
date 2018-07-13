"""Support for command-line interfaces."""

# Standard imports
import asyncio
import logging
try:
    import readline  # Import readline for better UX with input prompts
    readline
except ImportError:
    pass
import sys
from abc import abstractmethod

# Local package imports
from lhrhost.util.concurrency import Concurrent

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# Printing
CONSOLE_WIDTH = 6
CONSOLE_HEADER = (
    'Commands' + ('\t' * (CONSOLE_WIDTH - 1)) + 'Responses' + '\n' +
    ('-' * (12 * CONSOLE_WIDTH + 8))
)
RESPONSE_PREFIX = '\t' * CONSOLE_WIDTH


class Prompt:
    """Functor for async input.

    Reference:
        https://stackoverflow.com/a/35514777

    """

    def __init__(self, loop=None, end='\n', flush=False):
        """Initialize member variables."""
        if loop is None:
            loop = asyncio.get_event_loop()
        self.loop = loop
        self.input_queue = asyncio.Queue(loop=self.loop)
        self.loop.add_reader(sys.stdin, self.on_input)
        self.end = end
        self.flush = flush

    def on_input(self):
        """Put available input from stdin into the input queue."""
        asyncio.ensure_future(self.input_queue.put(sys.stdin.readline()), loop=self.loop)

    async def __call__(self, msg, end=None, flush=None):
        """Request user input like Python's built-in :fun:`input`."""
        if end is None:
            end = self.end
        if flush is None:
            flush = self.flush
        print(msg, end=end, flush=flush)
        input_line = await self.input_queue.get()
        return input_line.rstrip('\n')

    async def number(self, prompt_question, default_value=None):
        """Get an integer from the user."""
        while True:
            number = await self.__call__(
                '{} {}'.format(
                    prompt_question,
                    (
                        '[Default: {}] '.format(default_value)
                        if default_value is not None else ''
                    )
                )
            )
            if not number:
                return default_value
            try:
                number = int(number)
                return number
            except ValueError:
                print('Invalid input!')


class ConsoleManager(Concurrent):
    """Abstract class to manage console input asynchronously.

    Creates an asynchronous coroutine which reads lines from stdin on a separate
    thread and handles them.
    """

    def __init__(self, executor=None, ready_waiter=None):
        """Initialize member variables."""
        self.executor = executor
        self._loop = asyncio.get_event_loop()
        # Console prompt
        self._ready_waiter = ready_waiter
        self._console_prompt_task = None

    # Implement Concurrent

    def start(self):
        """Start the associated asynchronous tasks."""
        self._start_console_prompt_task()

    def stop(self):
        """Stop the associated asynchronous tasks."""
        if self._console_prompt_task is not None:
            self._console_prompt_task.cancel()

    # Console prompt

    def flush_console_input(self):
        """Clear all data in stdin."""
        try:
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getch()
        except ImportError:
            import sys
            import termios
            termios.tcflush(sys.stdin, termios.TCIOFLUSH)

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

    @abstractmethod
    async def on_console_ready(self):
        """Take some action when the console is ready."""
        pass

    async def _loop_console_prompt(self):
        """Monitor the transport actor and restart it when it dies."""
        if callable(self._ready_waiter):
            await self._ready_waiter()
            self.flush_console_input()
        await self.on_console_ready()
        logger.info('Ready for command-line input!')
        logger.info(
            'Enter commands as separate lines. '
            'To quit, enter a blank line or press Ctrl-D.'
        )
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
