"""
Device API wrapper for Cheese Core
"""

from java import jclass

# 导入 Java 类
CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
_device_cls = CoreFactory.INSTANCE.getDevice()

class device:


    def __init__(self):

        ...
    @staticmethod
    def getIMEI():
        """获取设备 IMEI"""
        return _device_cls.getIMEI()
    @staticmethod
    def getCpuArchitecture():
        """获取 CPU 架构"""
        return _device_cls.getCpuArchitecture()
    @staticmethod
    def getDeviceName():
        """获取设备名称"""
        return _device_cls.getDeviceName()
    @staticmethod
    def getBatteryLevel():
        """获取电池电量"""
        return _device_cls.getBatteryLevel()
    @staticmethod
    def getCpuModel():
        """获取 CPU 型号"""
        return _device_cls.getCpuModel()
    @staticmethod
    def getAppMD5():
        """获取应用 MD5"""
        return _device_cls.getAppMD5()
    @staticmethod
    def supportedOAID():
        """是否支持 OAID"""
        return _device_cls.supportedOAID()
    @staticmethod
    def getOAID():
        """获取 OAID"""
        return _device_cls.getOAID()
    @staticmethod
    def getPosition():
        """获取位置信息"""
        return _device_cls.getPosition()
    @staticmethod
    def getPublicIP(url):
        """获取公网 IP"""
        return _device_cls.getPublicIP(url)
    @staticmethod
    def getWifiIP():
        """获取 WiFi IP"""
        return _device_cls.getWifiIP()
    @staticmethod
    def getAndroidVersion():
        """获取 Android 版本"""
        return _device_cls.getAndroidVersion()
    @staticmethod
    def getStatusBarHeight():
        """获取状态栏高度"""
        return _device_cls.getStatusBarHeight()
    @staticmethod
    def getNavigationBarHeight():
        """获取导航栏高度"""
        return _device_cls.getNavigationBarHeight()
    @staticmethod
    def getScreenHeight():
        """获取屏幕高度"""
        return _device_cls.getScreenHeight()
    @staticmethod
    def getScreenWidth():
        """获取屏幕宽度"""
        return _device_cls.getScreenWidth()
    @staticmethod
    def isLandscape():
        """是否横屏"""
        return _device_cls.isLandscape()
    @staticmethod
    def getScreenDpi():
        """获取屏幕 DPI"""
        return _device_cls.getScreenDpi()
    @staticmethod
    def getTime():
        """获取当前时间"""
        return _device_cls.getTime()
    @staticmethod
    def getClipboard():
        """获取剪贴板内容"""
        return _device_cls.getClipboard()
    @staticmethod
    def setClipboard(text):
        """设置剪贴板内容"""
        return _device_cls.setClipboard(text)

