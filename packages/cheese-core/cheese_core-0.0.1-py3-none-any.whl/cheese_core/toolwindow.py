"""
ToolWindow API wrapper for Cheese Core
"""

from java import jclass

CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
_toolwindow_cls = CoreFactory.INSTANCE.getToolWindow()
class toolwindow:

    def __init__(self):
        ...
    @staticmethod
    def floatingLogcat():
        """
        获取浮动控制台实例
        :return: Console 对象
        """
        # Kotlin 直接 new Console(CoreEnv.envContext)
        # 这里如果 CoreFactory 提供直接接口可以用 _toolwindow.floatingConsole()
        # 否则直接 new Console
        return _toolwindow_cls.floatingLogcat()
    @staticmethod
    def floatingConsole():
        """
        获取浮动 Logcat 窗口实例
        :return: Logcat 对象
        """
        # Kotlin 直接 new Logcat(CoreEnv.envContext, null)
        return _toolwindow_cls.floatingConsole()
