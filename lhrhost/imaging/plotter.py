"""Support for plotting of images."""

# External imports
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

# Local package imports
from lhrhost.imaging.webcam import ImageReceiver
from lhrhost.dashboard import DocumentLayout, DocumentModel

# External imports
import numpy as np


class ImagePlot(DocumentLayout):
    """Plot of received images."""

    def __init__(self, width=640, height=360):
        """Initialize member variables."""
        super().__init__()
        self.width = width
        self.height = height

        self.image_source = ColumnDataSource({'image': []})
        self._init_image_plot()

    def _init_image_plot(self):
        """Initialize the image plot."""
        self.fig = figure(
            title='Image Captured from Camera',
            x_axis_location='above',
            width=self.width, height=self.height,
            x_range=[0, self.width], y_range=[self.height, 0]
        )
        self.image = None
        self.image = self.fig.image_rgba(
            image='image', x=0, y=self.height, dw=self.width, dh=self.height,
            source=self.image_source
        )

    def _convert_image(self, image_rgb):
        """Convert a floating-point RGB image to a uint8 image which can be plotted."""
        (height, width) = image_rgb.shape[:2]
        image_rgba = np.dstack((image_rgb, np.ones((height, width))))
        image_rgba *= 255
        image_rgba = image_rgba.astype(np.uint8)
        image_rgba = np.flipud(image_rgba)
        return image_rgba

    def update_image(self, image_rgb):
        """Receive and plot a floating-point RGB image given as a numpy array."""
        image_rgba = self._convert_image(image_rgb)
        (height, width) = image_rgba.shape[:2]
        self.image_source.data = {'image': [image_rgba]}

    # Implement DocumentLayout

    @property
    def layout(self):
        """Return a document layout element."""
        return self.fig


class ImagePlotter(DocumentModel, ImageReceiver):
    """Plotter of received images, synchronized across documents."""

    def __init__(self, *args, **kwargs):
        """Initialize member variables."""
        super().__init__(ImagePlot, *args, **kwargs)

    # Implement ImageReceiver

    async def on_image(self, image_rgb):
        """Receive and plot a floating-point RGB image given as a numpy array."""
        self.update_docs(lambda plot: plot.update_image(image_rgb))
