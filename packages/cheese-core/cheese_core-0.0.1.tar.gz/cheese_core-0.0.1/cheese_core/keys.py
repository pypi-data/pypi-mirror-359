

from java import jclass


# 引入 Cheese 核心工厂
CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
_keys_cls = CoreFactory.INSTANCE.getKeys()
class keys:
    """Keys 接口的 Python 封装类"""

    def __init__(self):
        # 通过 CoreFactory 获取 Keys 实例
        ...
    @staticmethod
    def home() -> bool:
        """模拟 Home 键"""
        return _keys_cls.home()
    @staticmethod
    def back() -> bool:
        """模拟返回键"""
        return _keys_cls.back()
    @staticmethod
    def quickSettings() -> bool:
        """打开快速设置"""
        return _keys_cls.quickSettings()
    @staticmethod
    def powerDialog() -> bool:
        """打开电源对话框"""
        return _keys_cls.powerDialog()
    @staticmethod
    def pullNotificationBar() -> bool:
        """下拉通知栏"""
        return _keys_cls.pullNotificationBar()
    @staticmethod
    def recents() -> bool:
        """打开最近任务"""
        return _keys_cls.recents()
    @staticmethod
    def lockScreen() -> bool:
        """锁屏，API 28+ 支持"""
        return _keys_cls.lockScreen()
    @staticmethod
    def screenShot() -> bool:
        """截图，API 28+ 支持"""
        return _keys_cls.screenShot()
    @staticmethod
    def splitScreen() -> bool:
        """分屏"""
        return _keys_cls.splitScreen()
