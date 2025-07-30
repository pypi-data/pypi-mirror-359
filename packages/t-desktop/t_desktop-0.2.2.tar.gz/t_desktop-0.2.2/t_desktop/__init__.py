"""Top-level package for t-desktop."""

__author__ = """Thoughtful"""
__email__ = "support@thoughtful.ai"
__version__ = "__version__ = '0.2.2'"

from .t_desktop import DesktopApp
from .decorators import relogin_and_retry_if_pywin_error, retry_if_pywin_error, capture_screenshot_if_pywin_error

__all__ = [
    "DesktopApp",
    "relogin_and_retry_if_pywin_error",
    "retry_if_pywin_error",
    "capture_screenshot_if_pywin_error",
]
