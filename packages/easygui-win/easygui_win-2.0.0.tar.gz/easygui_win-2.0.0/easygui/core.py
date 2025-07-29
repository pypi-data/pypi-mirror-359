#!/usr/bin/env python3
"""
EasyGUI - A super simple Windows GUI library
Author: Generated from optimized Windows API GUI code
License: MIT

The easiest way to create Windows GUI applications in Python!
No external dependencies - just pure Python.

Quick Start:
    import easygui as gui
    
    app = gui.App("My App")
    app.text("Hello World!")
    app.button("Click me!", lambda: print("Clicked!"))
    app.run()

Or use the decorator style:
    @gui.app("My App")
    def my_app():
        gui.text("Welcome!")
        gui.button("OK", gui.close)
"""

import ctypes
from ctypes import wintypes, byref, POINTER, Structure, c_int, c_long
import sys
from typing import List, Callable, Optional, Union, Any

__version__ = "2.0.0"
__all__ = ['App', 'app', 'text', 'button', 'space', 'close', 'Color']

# Windows API setup (same as before but hidden from user)
WNDPROC = ctypes.WINFUNCTYPE(c_long, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
WS_OVERLAPPEDWINDOW, WS_VISIBLE, SW_SHOW = 0x00CF0000, 0x10000000, 5
WM_DESTROY, WM_PAINT, WM_LBUTTONDOWN, WM_CLOSE = 0x0002, 0x000F, 0x0201, 0x0010
WHITE_BRUSH, TRANSPARENT = 0, 1

def LOWORD(dword):
    return dword & 0xFFFF

def HIWORD(dword):
    return (dword >> 16) & 0xFFFF


class WNDCLASS(Structure):
    _fields_ = [('style', wintypes.UINT), ('lpfnWndProc', WNDPROC), ('cbClsExtra', c_int),
                ('cbWndExtra', c_int), ('hInstance', wintypes.HINSTANCE), ('hIcon', wintypes.HICON),
                ('hCursor', wintypes.HANDLE), ('hbrBackground', wintypes.HBRUSH),
                ('lpszMenuName', wintypes.LPCWSTR), ('lpszClassName', wintypes.LPCWSTR)]

class RECT(Structure):
    _fields_ = [('left', c_int), ('top', c_int), ('right', c_int), ('bottom', c_int)]

class PAINTSTRUCT(Structure):
    _fields_ = [('hdc', wintypes.HDC), ('fErase', wintypes.BOOL), ('rcPaint', RECT),
                ('fRestore', wintypes.BOOL), ('fIncUpdate', wintypes.BOOL), ('rgbReserved', wintypes.BYTE * 32)]

class MSG(Structure):
    _fields_ = [('hwnd', wintypes.HWND), ('message', wintypes.UINT), ('wParam', wintypes.WPARAM),
                ('lParam', wintypes.LPARAM), ('time', wintypes.DWORD), ('pt', wintypes.POINT)]

user32, kernel32, gdi32 = ctypes.windll.user32, ctypes.windll.kernel32, ctypes.windll.gdi32

def _setup_api():
    gdi32.TextOutW.argtypes = [wintypes.HDC, c_int, c_int, wintypes.LPCWSTR, c_int]
    gdi32.SetTextColor.argtypes = [wintypes.HDC, wintypes.COLORREF]
    gdi32.SetBkMode.argtypes = [wintypes.HDC, c_int]
    user32.FillRect.argtypes = [wintypes.HDC, POINTER(RECT), wintypes.HBRUSH]
    user32.DefWindowProcW.restype = c_long
    user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]

_setup_api()

class Color:
    """Simple color class with presets."""
    def __init__(self, r: int, g: int, b: int):
        self.r, self.g, self.b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
    
    def to_colorref(self):
        return self.r | (self.g << 8) | (self.b << 16)
    
    # Color presets
    BLACK = None
    WHITE = None
    GRAY = None
    LIGHT_GRAY = None
    BLUE = None
    RED = None
    GREEN = None

# Initialize color presets
Color.BLACK = Color(0, 0, 0)
Color.WHITE = Color(255, 255, 255)
Color.GRAY = Color(128, 128, 128)
Color.LIGHT_GRAY = Color(240, 240, 240)
Color.BLUE = Color(100, 150, 255)
Color.RED = Color(255, 100, 100)
Color.GREEN = Color(100, 255, 100)

class _Widget:
    """Internal widget class - users don't need to know about this."""
    def __init__(self, x, y, width, height):
        self.x, self.y, self.width, self.height = x, y, width, height
        self.visible = True
        self.bg_color = Color.LIGHT_GRAY
        self.border_color = Color(180, 180, 180)
    
    def contains_point(self, px, py):
        return self.x <= px <= self.x + self.width and self.y <= py <= self.y + self.height
    
    def render(self, hdc):
        if not self.visible:
            return
        
        brush = gdi32.CreateSolidBrush(self.bg_color.to_colorref())
        pen = gdi32.CreatePen(0, 1, self.border_color.to_colorref())
        
        old_brush = gdi32.SelectObject(hdc, brush)
        old_pen = gdi32.SelectObject(hdc, pen)
        
        gdi32.Rectangle(hdc, self.x, self.y, self.x + self.width, self.y + self.height)
        
        gdi32.SelectObject(hdc, old_brush)
        gdi32.SelectObject(hdc, old_pen)
        gdi32.DeleteObject(brush)
        gdi32.DeleteObject(pen)

class _Button(_Widget):
    """Internal button class."""
    def __init__(self, x, y, width, height, text, callback):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.text_color = Color.BLACK
        self.bg_color = Color(225, 225, 225)
    
    def render(self, hdc):
        super().render(hdc)
        
        if self.text:
            gdi32.SetTextColor(hdc, self.text_color.to_colorref())
            gdi32.SetBkMode(hdc, TRANSPARENT)
            
            text_x = self.x + (self.width // 2) - (len(self.text) * 4)
            text_y = self.y + (self.height // 2) - 8
            
            gdi32.TextOutW(hdc, text_x, text_y, self.text, len(self.text))
    
    def handle_click(self):
        if self.callback:
            try:
                self.callback()
            except Exception as e:
                print(f"Button callback error: {e}")

class _Label(_Widget):
    """Internal label class."""
    def __init__(self, x, y, text, color=None):
        super().__init__(x, y, len(text) * 8 + 10, 25)
        self.text = text
        self.text_color = color or Color.BLACK
        self.bg_color = None  # Transparent
    
    def render(self, hdc):
        if self.text:
            gdi32.SetTextColor(hdc, self.text_color.to_colorref())
            gdi32.SetBkMode(hdc, TRANSPARENT)
            gdi32.TextOutW(hdc, self.x, self.y, self.text, len(self.text))

# Global state for the current app (makes the API super simple)
_current_app = None

class App:
    """
    The main application class. Super easy to use!
    
    Examples:
        app = App("My App")
        app.text("Hello!")
        app.button("OK", lambda: print("OK clicked"))
        app.run()
    """
    
    def __init__(self, title: str = "EasyGUI App", width: int = 600, height: int = 400):
        """Create a new app."""
        global _current_app
        _current_app = self
        
        self.title = title
        self.width = width
        self.height = height
        self.widgets = []
        self.hwnd = None
        self.running = False
        self.class_name = f"EasyGUI_{id(self)}"
        self._wnd_proc = WNDPROC(self._window_proc)
        
        # Auto-layout system
        self._current_y = 20
        self._margin = 20
        self._spacing = 10
        
        # Background color
        self.background = Color(250, 250, 250)
        
        # Callbacks
        self.on_close_callback = None
    
    def text(self, content: str, color: Optional[Color] = None) -> 'App':
        """
        Add text to the app.
        
        Args:
            content: The text to display
            color: Text color (optional)
        
        Returns:
            Self for method chaining
        """
        label = _Label(self._margin, self._current_y, content, color)
        self.widgets.append(label)
        self._current_y += 30
        return self
    
    def button(self, text: str, callback: Callable = None, width: int = 120) -> 'App':
        """
        Add a button to the app.
        
        Args:
            text: Button text
            callback: Function to call when clicked
            width: Button width in pixels
        
        Returns:
            Self for method chaining
        """
        if callback is None:
            callback = lambda: print(f"'{text}' clicked!")
        
        button = _Button(self._margin, self._current_y, width, 35, text, callback)
        self.widgets.append(button)
        self._current_y += 45
        return self
    
    def space(self, pixels: int = 20) -> 'App':
        """
        Add vertical space.
        
        Args:
            pixels: Amount of space to add
        
        Returns:
            Self for method chaining
        """
        self._current_y += pixels
        return self
    
    def on_close(self, callback: Callable):
        """Set a callback for when the window is closed."""
        self.on_close_callback = callback
        return self
    
    def close(self):
        """Close the application."""
        self.running = False
        if self.hwnd:
            user32.DestroyWindow(self.hwnd)
    
    def refresh(self):
        """Refresh the display."""
        if self.hwnd:
            user32.InvalidateRect(self.hwnd, None, True)
    
    def _window_proc(self, hwnd, msg, wparam, lparam):
        """Handle Windows messages."""
        try:
            if msg == WM_DESTROY:
                user32.PostQuitMessage(0)
                self.running = False
                if self.on_close_callback:
                    self.on_close_callback()
                return 0
            elif msg == WM_PAINT:
                ps = PAINTSTRUCT()
                hdc = user32.BeginPaint(hwnd, byref(ps))
                
                # Fill background
                rect = RECT()
                user32.GetClientRect(hwnd, byref(rect))
                brush = gdi32.CreateSolidBrush(self.background.to_colorref())
                user32.FillRect(hdc, byref(rect), brush)
                gdi32.DeleteObject(brush)
                
                # Render widgets
                for w in self.widgets:
                    w.render(hdc)
                
                user32.EndPaint(hwnd, byref(ps))
                return 0
            elif msg == WM_LBUTTONDOWN:
                x = LOWORD(lparam)
                y = HIWORD(lparam)
                for w in self.widgets:
                    if isinstance(w, _Button) and w.contains_point(x, y):
                        w.handle_click()
                        self.refresh()
                        break
                return 0
            elif msg == WM_CLOSE:
                self.close()
                return 0
            
            return user32.DefWindowProcW(hwnd, msg, wparam, lparam)
        except Exception as e:
            print(f"Window proc error: {e}")
            return user32.DefWindowProcW(hwnd, msg, wparam, lparam)
    
    def _register_class(self):
        hInstance = kernel32.GetModuleHandleW(None)
        wndClass = WNDCLASS()
        wndClass.style = 0
        wndClass.lpfnWndProc = self._wnd_proc
        wndClass.cbClsExtra = 0
        wndClass.cbWndExtra = 0
        wndClass.hInstance = hInstance
        wndClass.hIcon = None
        wndClass.hCursor = user32.LoadCursorW(None, 32512)  # IDC_ARROW
        wndClass.hbrBackground = gdi32.GetStockObject(WHITE_BRUSH)
        wndClass.lpszMenuName = None
        wndClass.lpszClassName = self.class_name
        
        if not user32.RegisterClassW(byref(wndClass)):
            raise RuntimeError("Failed to register window class")
    
    def _create_window(self):
        hInstance = kernel32.GetModuleHandleW(None)
        self.hwnd = user32.CreateWindowExW(
            0,
            self.class_name,
            self.title,
            WS_OVERLAPPEDWINDOW | WS_VISIBLE,
            100, 100,
            self.width,
            self.height,
            None, None, hInstance, None
        )
        if not self.hwnd:
            raise RuntimeError("Failed to create window")
        user32.ShowWindow(self.hwnd, SW_SHOW)
        user32.UpdateWindow(self.hwnd)
    
    def run(self):
        """Start the app event loop (blocking)."""
        self._register_class()
        self._create_window()
        
        self.running = True
        msg = MSG()
        
        while self.running:
            if user32.PeekMessageW(byref(msg), None, 0, 0, 1):
                user32.TranslateMessage(byref(msg))
                user32.DispatchMessageW(byref(msg))
            else:
                user32.WaitMessage()

def app(title: str = "EasyGUI App", width: int = 600, height: int = 400):
    """
    Decorator for simple GUI apps.
    
    Usage:
        @app("Hello World")
        def main():
            text("Welcome!")
            button("OK", close)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            global _current_app
            _current_app = App(title, width, height)
            result = func(*args, **kwargs)
            _current_app.run()
            return result
        return wrapper
    return decorator

# Module-level API functions that call current app's methods

def text(content: str, color: Optional[Color] = None):
    if _current_app:
        _current_app.text(content, color)

def button(text_str: str, callback: Callable = None):
    if _current_app:
        _current_app.button(text_str, callback)

def space(pixels: int = 20):
    if _current_app:
        _current_app.space(pixels)

def close():
    if _current_app:
        _current_app.close()
