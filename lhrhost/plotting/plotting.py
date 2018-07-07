"""Support for imaging from webcams."""

# Standard imports
from abc import abstractmethod

# External imports
from bokeh.client import push_session
from bokeh.plotting import curdoc

# Local package imports
from lhrhost.util.interfaces import InterfaceClass


# Bokeh document layout

class DocumentLayout(object, metaclass=InterfaceClass):
    """Interface for a class which can be put into a Bokeh document."""

    def show(self):
        """Create a standalone document."""
        self.session = push_session(curdoc(), session_id='main')
        self.session.show(self.layout)

    @property
    @abstractmethod
    def layout(self):
        """Return a document layout element."""
        pass
