"""Support for imaging from webcams."""

# External imports
import cv2 as cv

import numpy as np


class Camera(object):
    """Manages a camera."""

    def __init__(self, camera_index=0):
        """Initialize member variables."""
        self.camera_index = camera_index

    def capture_image(self):
        """Grab a frame from the camera."""
        success = False
        capture = cv.VideoCapture(self.camera_index)
        while not success:
            (success, frame_bgr) = capture.read()
        capture.release()
        frame_rgb = cv.cvtColor(frame_bgr, cv.COLOR_BGR2RGB)
        frame_rgb = frame_rgb.astype(np.float) / 255.0
        return frame_rgb
