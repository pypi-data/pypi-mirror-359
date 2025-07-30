from typing import List, Tuple
import numpy as np
from mss import mss
from mistercar_screenshooter.exceptions import CaptureError
from mistercar_screenshooter.platform.base import BasePlatformCapture


class MacOSCapture(BasePlatformCapture):
    """macOS-specific implementation of screen capture functionality using MSS."""

    def __init__(self, **kwargs):
        """
        Initialize macOS screen capture with MSS.

        All keyword arguments are passed to mss().
        See MSS documentation for available parameters.

        Args:
            **kwargs: Arguments passed directly to mss()
        """
        try:
            self.sct = mss(**kwargs)
        except Exception as e:
            raise CaptureError(f"Failed to initialize MSS: {e}")

    def capture_screen(self) -> np.ndarray:
        """Capture the entire screen."""
        try:
            monitor = self.sct.monitors[0]  # Full screen (all monitors)
            sct_img = self.sct.grab(monitor)
            return np.array(sct_img)
        except Exception as e:
            raise CaptureError(f"Failed to capture screen: {str(e)}")

    def capture_region(self, region: Tuple[int, int, int, int]) -> np.ndarray:
        """Capture a specific region of the screen."""
        try:
            sct_img = self.sct.grab(region)
            return np.array(sct_img)
        except Exception as e:
            raise CaptureError(f"Failed to capture region {region}: {str(e)}")

    def capture_window(self, window_title: str) -> np.ndarray:
        """
        Capture a specific window.

        Args:
            window_title: The title of the window to capture

        Returns:
            np.ndarray: The captured window image as a numpy array

        Raises:
            NotImplementedError: Window capture is not implemented for macOS
        """
        # Note: Window capture on macOS requires additional Quartz/Cocoa integration
        raise NotImplementedError("Window capture is not implemented for macOS")

    def list_monitors(self) -> List[dict]:
        """
        List all available monitors.

        Returns:
            List[dict]: List of dictionaries containing monitor information
        """
        try:
            return self.sct.monitors[1:]  # Exclude the "all in one" monitor at index 0
        except Exception as e:
            raise CaptureError(f"Failed to list monitors: {str(e)}")

    def capture_monitor(self, monitor_id: int) -> np.ndarray:
        """Capture a specific monitor."""
        try:
            monitor = self.sct.monitors[monitor_id]
            sct_img = self.sct.grab(monitor)
            return np.array(sct_img)
        except IndexError:
            raise CaptureError(f"Monitor {monitor_id} not found")
        except Exception as e:
            raise CaptureError(f"Failed to capture monitor {monitor_id}: {str(e)}")
