"""Support for imaging from webcams."""

# Standard imports
import logging
from abc import abstractmethod
from functools import partial

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
        self.document = None

    def update_doc(self, callback):
        """Run a callback on the document.

        The callback should take no arguments.
        """
        self.document.add_next_tick_callback(callback)

    def initialize_doc(self, doc):
        """Initialize the provided document."""
        if self.document is None:
            self.set_doc(doc)
            doc.add_root(self.layout)
        else:
            logger.warning('Can only open one copy of the document!')

    def set_doc(self, doc):
        """Set the provided document to be the parent document."""
        self.document = doc

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

    def update_docs(self, callback):
        """Run a callback on all documents.

        The callback should take exactly one argument, the DocumentLayout instance.
        """
        for doc_layout in self.doc_layouts:
            doc_layout.document.add_next_tick_callback(partial(callback, doc_layout))

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
