"""Test webcam image capture."""

# Standard imports
import asyncio
import logging

# External imports
from bokeh import layouts
from bokeh.models import widgets

# Local package imports
from lhrhost.imaging.plotter import ImagePlotter
from lhrhost.imaging.webcam import Camera, ImageReceiver
from lhrhost.plotting import DocumentLayout, DocumentModel
from lhrhost.util.cli import Prompt

# Logging
logging.basicConfig(level=logging.INFO)


class CaptureButton(DocumentModel, ImageReceiver):
    """Webcam capture button, synchronized across documents."""

    def __init__(self, camera):
        """Initialize member variables."""
        super().__init__(widgets.Button, label='Capture image')
        self.camera = camera

    def capture_image(self):
        """Capture a new image."""
        def update(button):
            button.label = 'Capturing image...'
            button.disabled = True
        self.update_docs(update)

        asyncio.get_event_loop().create_task(self.camera.capture_image())

    # Implement DocumentModel

    def make_document_layout(self):
        """Return a new document layout instance."""
        layout = super().make_document_layout()
        layout.on_click(self.capture_image)
        return layout

    # Implement ImageReceiver

    async def on_image(self, image_rgb):
        """Update button state in response to received image."""
        def update(button):
            button.label = 'Capture image'
            button.disabled = False
        self.update_docs(update)


class WebcamController(DocumentLayout):
    """Webcam controller."""

    def __init__(self, image_model, button_model):
        """Initialize member variables."""
        super().__init__()

        self.capture_button = button_model.make_document_layout()
        self.image_plot = image_model.make_document_layout()

        self._init_controller_widgets()
        self.column_layout = layouts.column([
            self.controller_widgets, self.image_plot.layout
        ])

    def _init_controller_widgets(self):
        """Initialize the webcam capture button."""
        self.controller_widgets = layouts.widgetbox([
            widgets.Div(text='<h1>Webcam</h1>'),
            self.capture_button
        ])

    # Implement DocumentLayout

    @property
    def layout(self):
        """Return a document layout element."""
        return self.column_layout

    def initialize_doc(self, doc):
        """Initialize the provided document."""
        super().initialize_doc(doc)
        self.image_plot.set_doc(self.document)


class WebcamModel(DocumentModel):
    """Webcam controller, synchronized across documents."""

    def __init__(self, camera, *args, **kwargs):
        """Initialize member variables."""
        self.button_model = CaptureButton(camera)
        self.image_model = ImagePlotter()
        camera.image_receivers.append(self.image_model)
        camera.image_receivers.append(self.button_model)
        super().__init__(
            WebcamController, self.image_model, self.button_model, *args, **kwargs
        )


def main():
    """Take an image and show it in Bokeh."""
    camera = Camera()
    model = WebcamModel(camera)

    camera.open(1)

    model.show()
    model.server.run_until_shutdown()

    camera.close()


if __name__ == '__main__':
    main()
