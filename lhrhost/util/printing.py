"""Various utilities for printing to stdout."""
from typing import Any


# Basic printing

class Printer(object):
    """Simple class which provides a mechanism for printing things."""

    def __init__(self, prefix='', suffix='\n'):
        """Initialize member variables."""
        self._prefix = prefix
        self._suffix = suffix

    def print(self, content: Any) -> None:
        """Print some content."""
        print(self._prefix, end='')
        print(content, end='')
        print(self._suffix, end='')
