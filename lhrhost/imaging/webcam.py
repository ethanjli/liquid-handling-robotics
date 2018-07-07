"""Support for imaging from webcams."""

# Standard imports
import asyncio
import logging
from abc import abstractmethod
from typing import Iterable, List, Optional

# External imports
import cv2 as cv

# Local package imports
from lhrhost.util.interfaces import InterfaceClass

# External imports
import numpy as np

# Logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# Receipt of images

class ImageReceiver(object, metaclass=InterfaceClass):
    """Interface for a class which receives floating-point RGB images."""

    @abstractmethod
    async def on_image(self, image) -> None:
        """Receive and handle a floating-point RGB image as a numpy array."""
        pass


# Type-checking names
_ImageReceivers = Iterable[ImageReceiver]


# Acquisition of images

class Camera(object):
    """Manages a camera."""

    def __init__(
        self, image_receivers: Optional[_ImageReceivers]=None
    ):
        """Initialize member variables."""
        self.capture = None
        self.image_receivers: List[ImageReceiver] = []
        if image_receivers:
            self.image_receivers = [
                receiver for receiver in image_receivers
            ]

    def open(self, camera_index=0):
        """Try to start a capture with the specified camera index."""
        while True:
            capture = cv.VideoCapture(camera_index)
            if capture.isOpened():
                self.capture = capture
                break
            logger.error(
                'Camera {} unavailable! Trying with camera {} instead...'.format(
                    camera_index, camera_index - 1
                )
            )
            camera_index -= 1
        self.acquire_image()

    def close(self):
        """Stop a capture."""
        if self.capture is not None:
            self.capture.release()
        self.capture = None

    def acquire_image(self, width=640, height=360):
        """Grab a frame from the camera."""
        if self.capture is None:
            logger.error('Camera needs to be opened before capturing images!')
            return None

        self.capture.set(cv.CAP_PROP_FRAME_WIDTH, width)
        self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, height)

        success = False
        while not success:
            (success, frame_bgr) = self.capture.read()

        frame_rgb = cv.cvtColor(frame_bgr, cv.COLOR_BGR2RGB)
        frame_rgb = frame_rgb.astype(np.float) / 255.0
        return frame_rgb

    async def capture_image(self, **kwargs):
        """Grab a frame from the camera and forward it to receivers."""
        frame_rgb = self.acquire_image(**kwargs)
        await asyncio.gather(*[
            receiver.on_image(frame_rgb)
            for receiver in self.image_receivers
        ])
        return frame_rgb
