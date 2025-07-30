"""
APP API wrapper for Cheese Core
"""

from java import jclass

# 引入 Cheese 核心工厂
CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
_app_cls = CoreFactory.INSTANCE.getAPP()

class app:
    """APP 接口的 Python 封装类"""


    def __init__():
        # 通过 CoreFactory 获取 APP 实例
        ...
    @staticmethod
    def getForegroundPkg():
        """
        获取当前前台应用包名
        """
        return _app_cls.getForegroundPkg()
    @staticmethod
    def openUrl(url):
        """
        打开指定 URL
        """
        _app_cls.openUrl(url)
    @staticmethod
    def uninstall(packageName):
        """
        卸载指定包名的应用
        """
        _app_cls.uninstall(packageName)
    @staticmethod
    def getPackageName(appName):
        """
        通过应用名称获取包名
        """
        return _app_cls.getPackageName(appName)
    @staticmethod
    def getAppName(packageName):
        """
        通过包名获取应用名称
        """
        return _app_cls.getAppName(packageName)
    @staticmethod
    def openAppSettings(packageName):
        """
        打开应用的系统设置界面
        """
        return _app_cls.openAppSettings(packageName)
    @staticmethod
    def openApp(packageName):
        """
        打开指定包名的应用
        """
        return _app_cls.openApp(packageName)
    @staticmethod
    def openScheme(schemeUri):
        """
        打开指定 scheme 协议
        """
        return _app_cls.openScheme(schemeUri)
    @staticmethod
    def getApkSha256(filePath):
        """
        获取 APK 的 SHA-256
        """
        return _app_cls.getApkSha256(filePath)
