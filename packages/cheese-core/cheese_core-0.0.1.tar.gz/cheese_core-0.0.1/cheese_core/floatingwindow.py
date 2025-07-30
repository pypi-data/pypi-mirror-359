"""
FloatingWindow API wrapper for Cheese Core
"""

from java import jclass

# 引入 Cheese 核心工厂
CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
_floatingwindow_cls = CoreFactory.INSTANCE.getFloatingWindow()

class floatingwindow:



    def __init__(self):
        self._floatingwindow = CoreFactory.INSTANCE.createFloatingWindow()

    def with_(self):
        """
        创建 EasyWindow 对象（调用 with()）
        """
        self.easyWindow = self._floatingwindow.with_()
        return self.easyWindow

    @staticmethod
    def recycleAll():
        _floatingwindow_cls.recycleAll()

    @staticmethod
    def cancelAll():
        _floatingwindow_cls.cancelAll()

    @staticmethod
    def requestPermission(timeout: int) -> bool:
        return _floatingwindow_cls.requestPermission(timeout)

    @staticmethod
    def checkPermission() -> bool:
        return _floatingwindow_cls.checkPermission()

    def show(self):
        """
        在 UI 线程显示浮窗
        """
        self._floatingwindow.show(self.easyWindow)

    def recycle(self):
        """
        在 UI 线程回收浮窗资源
        """
        self._floatingwindow.recycle(self.easyWindow)

    def cancel(self):
        """
        在 UI 线程取消浮窗显示
        """
        self._floatingwindow.cancel(self.easyWindow)
