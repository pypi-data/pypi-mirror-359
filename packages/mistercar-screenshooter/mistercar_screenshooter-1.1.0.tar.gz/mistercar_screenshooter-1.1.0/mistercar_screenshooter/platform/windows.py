import ctypes
import ctypes.wintypes
import warnings
from typing import List, Tuple, Any

import bettercam
import numpy as np
import win32gui
import win32ui

from mistercar_screenshooter.exceptions import WindowNotFoundError, CaptureError
from mistercar_screenshooter.platform.base import BasePlatformCapture


class WindowsCapture(BasePlatformCapture):
    """Windows-specific implementation of screen capture functionality using BetterCam."""

    def __init__(self, **kwargs):
        """
        Initialize Windows screen capture with BetterCam.

        All keyword arguments are passed to bettercam.create().
        Common BetterCam arguments include:
        - device_idx: Device index for capture (default: 0)
        - output_idx: Output index for multi-monitor setups (default: None)
        - output_color: Color format - "RGB", "BGR", "BGRA" (default: "RGB")
        - nvidia_gpu: Whether to use NVIDIA GPU acceleration (default: False)
        - max_buffer_len: Maximum buffer length for frame buffering (default: 64)

        Args:
            **kwargs: Arguments passed directly to bettercam.create()

        Raises:
            CaptureError: If BetterCam initialization fails
        """
        # Store kwargs for potential recreation (like monitor capture)
        self._kwargs = kwargs.copy()

        # Set sensible defaults for common parameters if not provided
        bettercam_kwargs = {
            "device_idx": 0,
            "output_color": "RGB",
            "nvidia_gpu": False,
            "max_buffer_len": 64,
            **kwargs  # User kwargs override defaults
        }

        try:
            self.camera = bettercam.create(**bettercam_kwargs)
        except Exception as e:
            # If nvidia_gpu was explicitly set to True and failed, try fallback
            if bettercam_kwargs.get("nvidia_gpu", False):
                try:
                    warnings.warn(f"NVIDIA GPU capture failed, falling back to software capture: {e}")
                    fallback_kwargs = bettercam_kwargs.copy()
                    fallback_kwargs["nvidia_gpu"] = False
                    self.camera = bettercam.create(**fallback_kwargs)
                    self._kwargs["nvidia_gpu"] = False  # Update stored kwargs
                except Exception as fallback_e:
                    raise CaptureError(
                        f"Failed to initialize BetterCam with GPU ({e}) and software fallback ({fallback_e})")
            else:
                raise CaptureError(f"Failed to initialize BetterCam: {e}")

    def capture_screen(self) -> np.ndarray:
        """Capture the entire screen."""
        try:
            return self.camera.grab()
        except Exception as e:
            raise CaptureError(f"Failed to capture screen: {str(e)}")

    def capture_region(self, region: Tuple[int, int, int, int]) -> np.ndarray:
        """Capture a specific region of the screen."""
        try:
            return self.camera.grab(region=region)
        except Exception as e:
            raise CaptureError(f"Failed to capture region {region}: {str(e)}")

    def capture_window(self, window_title: str) -> np.ndarray:
        """Capture a specific window using Win32 API."""
        try:
            hwnd = win32gui.FindWindow(None, window_title)
            if not hwnd:
                raise WindowNotFoundError(f"Window not found: {window_title}")

            rect = win32gui.GetWindowRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]

            if width <= 0 or height <= 0:
                raise CaptureError(f"Invalid window dimensions: {width}x{height}")

            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)

            result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)
            if result == 0:
                raise CaptureError(f"Failed to capture window: {window_title}")

            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)

            img = np.frombuffer(bmpstr, dtype=np.uint8).reshape(height, width, 4)

            # Cleanup Windows resources
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            return img[:, :, [2, 1, 0]]  # Convert BGRA to RGB (remove alpha channel)

        except WindowNotFoundError:
            raise
        except Exception as e:
            raise CaptureError(f"Failed to capture window '{window_title}': {str(e)}")

    def list_monitors(self) -> List[dict]:
        """List all available monitors."""
        try:
            from mss import mss
            return mss().monitors[1:]  # Exclude the "all in one" monitor at index 0
        except Exception as e:
            raise CaptureError(f"Failed to list monitors: {str(e)}")

    def capture_monitor(self, monitor_id: int) -> np.ndarray:
        """Capture a specific monitor."""
        try:
            # Create new camera instance for monitor capture
            # Use stored kwargs but override output_idx with monitor_id
            monitor_kwargs = self._kwargs.copy()
            monitor_kwargs['output_idx'] = monitor_id

            camera = bettercam.create(**monitor_kwargs)
            return camera.grab()
        except Exception as e:
            raise CaptureError(f"Failed to capture monitor {monitor_id}: {str(e)}")
