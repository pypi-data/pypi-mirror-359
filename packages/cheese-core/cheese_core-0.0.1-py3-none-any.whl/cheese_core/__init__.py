"""
Cheese Core - Python wrapper for net.codeocean.cheese.core
"""


from .adb import adb
from .app import app
from .assets import assets
from .base import base
from .canvas import canvas
from .color import color
from .converters import converters
from .device import device
from .env import env
from .events import events
from .files import files
from .floatingwindow import floatingwindow
from .http import http
from .image import image
from .keyboard import keyboard
from .keys import keys
from .ocr import ocr
from .path import path
from .permissions import permissions
from .persistentstore import persistentstore
from .plugins import plugins
from .point import point
from .recordscreen import recordscreen
from .root import root
from .thread import thread
from .toolwindow import toolwindow
from .uinode import uinode,AccessibilityNodeInfoCompat
from .websocket import websocket
from .webview import webview
from .yolo import yolo
from .zip import zip

# 导出所有主要接口
__all__ = [
    'AccessibilityNodeInfoCompat',
    'adb',
    'app',
    'assets',
    'base',
    'canvas',
    'color',
    'converters',
    'device',
    'env',
    'events',
    'files',
    'floatingwindow',
    'http',
    'image',
    'keyboard',
    'keys',
    'ocr',
    'path',
    'permissions',
    'persistentstore',
    'plugins',
    'point',
    'recordscreen',
    'root',
    'thread',
    'toolwindow',
    'uinode',
    'websocket',
    'webview',
    'yolo',
    'zip',
    'converters'
]

# 版本信息
__version__ = "1.0.0"

#
# @property
# def newDevice(self):
#     """获取 Device 包装器实例"""
#     if self._device_wrapper is None:
#         self._device_wrapper = DeviceWrapper()
#     return self._device_wrapper
#
#
# @property
# def newBase(self):
#     """获取 Device 包装器实例"""
#     if self._base_wrapper is None:
#         self._base_wrapper = BaseWrapper()
#     return self._base_wrapper
#
#
# @property
# def newCanvas(self):
#     """获取 Device 包装器实例"""
#     if self._canvas_wrapper is None:
#         self._canvas_wrapper = CanvasWrapper()
#     return self._canvas_wrapper
