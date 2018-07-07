"""Test webcam image capture."""

# Standard imports
import asyncio

# Local package imports
from lhrhost.imaging.plotter import ImagePlotter
from lhrhost.imaging.webcam import Camera


def main():
    """Take an image and show it in Bokeh."""
    plotter = ImagePlotter()
    camera = Camera(1, image_receivers=[plotter])
    loop = asyncio.get_event_loop()
    task = loop.create_task(camera.capture_image())
    loop.run_until_complete(task)
    plotter.show()


if __name__ == '__main__':
    main()
