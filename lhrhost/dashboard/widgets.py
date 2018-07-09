"""Document layouts for Bokeh widgets."""

# Standard impots
from abc import abstractmethod

# External imports
from bokeh.models import ColumnDataSource, callbacks, widgets

# Local package imports
from lhrhost.dashboard import DocumentModel
from lhrhost.util.interfaces import InterfaceClass


class Button(DocumentModel, metaclass=InterfaceClass):
    """Button mix-in, synchronized across documents."""

    def __init__(self, *args, **kwargs):
        """Initialize member variables."""
        super().__init__(widgets.Button, *args, **kwargs)

    def disable_button(self, label):
        """Disable the button."""
        def update(button):
            button.label = label
            button.disabled = True
        self.update_docs(update)

    def enable_button(self, label):
        """Disable the button."""
        def update(button):
            button.label = label
            button.disabled = False
        self.update_docs(update)

    @abstractmethod
    def on_click(self):
        """Handle a button click event."""
        pass

    # Implement DocumentModel

    def make_document_layout(self):
        """Return a new document layout instance."""
        layout = super().make_document_layout()
        layout.on_click(self.on_click)
        return layout


class Slider(DocumentModel, metaclass=InterfaceClass):
    """Slider mix-in, synchronized across documents.

    Only triggers updates on mouseup.
    Also works with BokekhRangeSlider widgets.
    """

    def __init__(
        self, initial_title, *args, slider_widget_class=widgets.Slider, **kwargs
    ):
        """Initialize member variables."""
        super().__init__(slider_widget_class, *args, **kwargs)
        self.initial_title = initial_title
        self.value_source = ColumnDataSource({'value': []})
        self.value_source.on_change('data', self.on_value_change)

    def disable_slider(self, title):
        """Disable the slider."""
        def update(slider):
            slider.title = title
            slider.disabled = True
        self.update_docs(update)

    def enable_slider(self, title, new_value=None):
        """Enable the slider."""
        def update(slider):
            slider.title = title
            slider.disabled = False
            if new_value is not None:
                slider.value = new_value
        self.update_docs(update)

    @abstractmethod
    def on_value_change(self, attr, old, new):
        """Handle a slider value change mouseup event."""
        pass

    # Implement DocumentModel

    def make_document_layout(self):
        """Return a new document layout instance."""
        layout = super().make_document_layout()
        # Callback mouseup workaround from https://stackoverflow.com/a/38379136
        layout.callback_policy = 'mouseup'
        layout.callback = callbacks.CustomJS(
            args={'source': self.value_source},
            code='source.data = {value: [cb_obj.value]}'
        )
        layout.show_value = True
        layout.title = self.initial_title
        layout.disabled = True
        return layout
