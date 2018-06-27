"""Various utilities for concurrency."""

# Standard imports
from abc import abstractmethod

# Local package imports
from lhrhost.util.interfaces import InterfaceClass


# Interfaces for actors and actor-like async routines

class Concurrent(object, metaclass=InterfaceClass):
    """Interface for a class which can start and stop concurrent work."""

    @abstractmethod
    def start(self):
        """Start concurrent work without blocking on completion of work."""
        pass

    @abstractmethod
    def stop(self):
        """Stop concurrent work without blocking on completion of work."""
        pass
