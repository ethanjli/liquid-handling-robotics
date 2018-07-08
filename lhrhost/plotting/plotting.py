"""Support for imaging from webcams."""

# Standard imports
import logging
from abc import abstractmethod

# External imports
from bokeh.server.server import Server

# Local package imports
from lhrhost.util.interfaces import InterfaceClass

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# Bokeh document layout

class DocumentLayout(object, metaclass=InterfaceClass):
    """Interface for a class which specifies the layout of a single Bokeh document."""

    def __init__(self):
        """Initialize member variables."""
        self.doc = None

    def update_doc(self, callback):
        """Run a callback on the document."""
        self.doc.add_next_tick_callback(callback)

    def initialize_doc(self, doc):
        """Initialize the provided document."""
        if self.doc is None:
            doc.add_root(self.layout)
            self.doc = doc
        else:
            logger.warning('Can only open one copy of the document!')

    def show(self, route='/', address='localhost', port=5006):
        """Create a standalone singleton document."""
        self.server = Server({route: self.initialize_doc}, address=address, port=port)
        self.server.start()
        logger.info('Serving document at {}:{}{}'.format(
            self.server.address, self.server.port, route
        ))
        self.server.show(route)

    @abstractmethod
    def layout(self):
        """Return a document layout element."""
        pass


class DocumentModel(object):
    """Mix-in for a class which specifies the layout of multiple Bokeh documents."""

    def __init__(self, document_layout_class: DocumentLayout, *args, **kwargs):
        """Initialize member variables."""
        self.doc_layouts = []
        self.document_layout_class: DocumentLayout = document_layout_class
        self.args = args
        self.kwargs = kwargs

    def make_document_layout(self):
        """Return a new document layout instance."""
        return self.document_layout_class(*self.args, **self.kwargs)

    def initialize_doc(self, doc):
        """Initialize the provided document."""
        doc_layout = self.make_document_layout()
        doc_layout.initialize_doc(doc)
        self.doc_layouts.append(doc_layout)

    def show(self, route='/', address='localhost', port=5006):
        """Create a standalone document for each connection.

        Each document, after it is created, will receive every data/model update
        received by every other document.
        """
        self.server = Server({route: self.initialize_doc}, address=address, port=port)
        self.server.start()
        logger.info('Serving document at {}:{}{}'.format(
            self.server.address, self.server.port, route
        ))
        self.server.show(route)
