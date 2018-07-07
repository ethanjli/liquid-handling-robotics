"""Support for plotting of images."""

# External imports
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

# Local package imports
from lhrhost.imaging.webcam import ImageReceiver
from lhrhost.plotting import DocumentLayout

# External imports
import numpy as np


class ImagePlotter(ImageReceiver, DocumentLayout):
    """Plots received images."""

    def __init__(self, width=640, height=360):
        """Initialize member variables."""
        self.width = width
        self.height = height

        self.plot_source = ColumnDataSource({'image': []})
        self.fig = figure(
            title='Image Captured from Camera',
            x_axis_location='above',
            width=self.width, height=self.height,
            x_range=[0, self.width], y_range=[self.height, 0]
        )
        self.image = None
        self.image = self.fig.image_rgba(
            image='image', x=0, y=self.height, dw=self.width, dh=self.height,
            source=self.plot_source
        )

        self.session = None

    def convert_image(self, image_rgb):
        """Convert a floating-point RGB image to a uint8 image which can be plotted."""
        (height, width) = image_rgb.shape[:2]
        image_rgba = np.dstack((image_rgb, np.ones((height, width))))
        image_rgba *= 255
        image_rgba = image_rgba.astype(np.uint8)
        image_rgba = np.flipud(image_rgba)
        return image_rgba

    async def on_image(self, image_rgb):
        """Receive and plot a floating-point RGB image given as a numpy array."""
        image_rgba = self.convert_image(image_rgb)
        (height, width) = image_rgba.shape[:2]
        self.plot_source.data = {'image': [image_rgba]}

    # Implement DocumentLayout

    @property
    def layout(self):
        """Return a document layout element."""
        return self.fig
