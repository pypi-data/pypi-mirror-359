"""
EasyGUI - A super simple Windows GUI library
"""

from .core import (
    App, app, text, button, space, close, Color,
    __version__, __all__
)

# Re-export everything for easy importing
__all__ = [
    'App', 'app', 'text', 'button', 'space', 'close', 'Color'
]

__version__ = "2.0.0"