
from java import jclass
from java.io import File

CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")

_plugins_cls = CoreFactory.INSTANCE.getPlugins()
class plugins:


    def __init__(self):
        self._plugins = CoreFactory.INSTANCE.createPlugins()

    def install(self, apk_path: str) -> bool:
        """
        安装插件APK
        :param apk_path: apk文件路径
        :return: 是否安装成功
        """
        return self._plugins.install(apk_path)

    def uninstall(self) -> bool:
        """
        卸载当前插件
        :return: 是否卸载成功
        """
        return self._plugins.uninstall()

    def createContext(self):
        """
        创建插件资源上下文
        :return: Android Context对象
        """
        return self._plugins.createContext()

    def getClassLoader(self):
        """
        获取插件的ClassLoader
        :return: ClassLoader对象
        """
        return self._plugins.getClassLoader()

    @staticmethod
    def hasPlugins(pkg: str):
        """
        获取插件的ClassLoader
        :return: ClassLoader对象
        """
        return _plugins_cls.hasPlugins(pkg)
