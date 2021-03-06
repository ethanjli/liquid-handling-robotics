"""Test webcam image capture."""

# Standard imports
import asyncio
import logging

# External imports
from bokeh import layouts
from bokeh.models import widgets

# Local package imports
from lhrhost.dashboard import DocumentLayout, DocumentModel
from lhrhost.dashboard.widgets import Button
from lhrhost.imaging.plotter import ImagePlotter
from lhrhost.imaging.webcam import Camera, ImageReceiver

# Logging
logging.basicConfig(level=logging.INFO)


class CaptureButton(Button, ImageReceiver):
    """Webcam capture button, synchronized across documents."""

    def __init__(self, camera):
        """Initialize member variables."""
        super().__init__(label='Capture image')
        self.camera = camera

    # Implement Button

    def on_click(self):
        """Handle a button click event."""
        self.disable_button('Capturing image...')
        asyncio.get_event_loop().create_task(self.camera.capture_image())

    # Implement ImageReceiver

    async def on_image(self, image_rgb):
        """Update button state in response to received image."""
        self.enable_button('Capture image')


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

    def initialize_doc(self, doc, as_root=False):
        """Initialize the provided document."""
        super().initialize_doc(doc, as_root)
        self.image_plot.initialize_doc(self.document)


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
