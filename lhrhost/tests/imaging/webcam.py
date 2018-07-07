"""Test webcam image capture."""

# Standard imports
import asyncio

# Local package imports
from lhrhost.imaging.plotter import ImagePlotter
from lhrhost.imaging.webcam import Camera
from lhrhost.util.cli import Prompt


async def acquire_images(camera):
    """Acquire a few images."""
    prompt = Prompt()
    await prompt('Press enter to capture an image: ')
    await camera.capture_image()
    await prompt('Press enter to capture another image: ')
    await camera.capture_image()


def main():
    """Take an image and show it in Bokeh."""
    plotter = ImagePlotter()
    plotter.show()
    camera = Camera(image_receivers=[plotter])
    camera.open(1)
    loop = asyncio.get_event_loop()
    task = loop.create_task(acquire_images(camera))
    loop.run_until_complete(task)
    camera.close()


if __name__ == '__main__':
    main()
