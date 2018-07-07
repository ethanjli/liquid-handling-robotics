"""Test webcam image capture."""

# External imports
from bokeh.client import push_session
from bokeh.plotting import curdoc, figure

# Local package imports
from lhrhost.imaging.webcam import Camera

# External imports
import numpy as np


def main():
    """Take an image and show it in Bokeh."""
    camera = Camera(1)
    image_rgb = camera.capture_image()
    fig = figure(
        title='Image Captured from Camera',
        x_axis_location='above',
        x_range=[0, image_rgb.shape[0]], y_range=[image_rgb.shape[1], 0]
    )
    image_rgba = np.concatenate(
        (
            image_rgb,
            np.ones((image_rgb.shape[0], image_rgb.shape[1], 1))
        ),
        axis=2
    )
    image_rgba *= 255
    image_rgba = image_rgba.astype(np.uint8)
    image_rgba = np.flipud(image_rgba)
    fig.image_rgba(
        image=[image_rgba],
        x=[0], y=[image_rgba.shape[1]],
        dw=[image_rgba.shape[0]], dh=[image_rgba.shape[1]]
    )
    session = push_session(curdoc(), session_id='main')
    session.show(fig)


if __name__ == '__main__':
    main()
