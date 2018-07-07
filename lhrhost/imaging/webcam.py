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
        self, camera_index=0, image_receivers: Optional[_ImageReceivers]=None
    ):
        """Initialize member variables."""
        self.camera_index = camera_index
        self.image_receivers: List[ImageReceiver] = []
        if image_receivers:
            self.image_receivers = [
                receiver for receiver in image_receivers
            ]

    def start_capture(self):
        """Try to start a cature with the specified index."""
        camera_index = self.camera_index
        while True:
            capture = cv.VideoCapture(camera_index)
            if capture.isOpened():
                return capture
            logger.error(
                'Camera {} unavailable! Trying with camera {} instead...'.format(
                    camera_index, camera_index - 1
                )
            )
            camera_index -= 1

    async def capture_image(self):
        """Grab a frame from the camera."""
        capture = self.start_capture()
        success = False
        while not success:
            (success, frame_bgr) = capture.read()
        capture.release()
        frame_rgb = cv.cvtColor(frame_bgr, cv.COLOR_BGR2RGB)
        frame_rgb = frame_rgb.astype(np.float) / 255.0
        await asyncio.gather(*[
            receiver.on_image(frame_rgb)
            for receiver in self.image_receivers
        ])
        return frame_rgb
