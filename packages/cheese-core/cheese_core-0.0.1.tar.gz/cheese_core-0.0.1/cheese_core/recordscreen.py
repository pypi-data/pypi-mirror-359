"""
RecordScreen API wrapper for Cheese Core
"""

from java import jclass

CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
_recordscreen_cls = CoreFactory.INSTANCE.getRecordScreen()
class recordscreen:

    def __init__(self):
        ...
    @staticmethod
    def requestPermission( timeout: int) -> bool:
        """
        请求录屏权限，超时单位秒
        """
        return _recordscreen_cls.requestPermission(timeout)
    @staticmethod
    def checkPermission() -> bool:
        """
        检查录屏权限
        """
        return _recordscreen_cls.checkPermission()
    @staticmethod
    def captureScreen(timeout: int, x: int, y: int, ex: int, ey: int):
        """
        截屏，返回 Bitmap 对象
        timeout: 超时
        x, y: 起始坐标
        ex, ey: 结束坐标
        """
        return _recordscreen_cls.captureScreen(timeout, x, y, ex, ey)
