"""Test webcam image capture."""

# Standard imports
import asyncio
import logging

# Local package imports
from lhrhost.imaging.plotter import ImagePlotter
from lhrhost.imaging.webcam import Camera
from lhrhost.util.cli import Prompt

# Logging
logging.basicConfig(level=logging.INFO)


async def acquire_images(camera):
    """Acquire a few images."""
    prompt = Prompt()
    await asyncio.sleep(2.0)
    await prompt('Press enter to capture an image: ')
    await camera.capture_image()
    await prompt('Press enter to capture another image: ')
    await camera.capture_image()


def main():
    """Take an image and show it in Bokeh."""
    loop = asyncio.get_event_loop()

    plotter = ImagePlotter()

    camera = Camera(image_receivers=[plotter])
    camera.open(1)

    plotter.show()
    task = loop.create_task(acquire_images(camera))

    loop.run_until_complete(task)

    plotter.server.stop()
    camera.close()


if __name__ == '__main__':
    main()
