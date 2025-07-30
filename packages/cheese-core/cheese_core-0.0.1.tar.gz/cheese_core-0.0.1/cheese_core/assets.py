"""
Assets API wrapper for Cheese Core
"""

from java import jclass

# 引入 Cheese 核心工厂
CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")

_assets_cls = CoreFactory.INSTANCE.getAssets()
class assets:
    """Assets 接口的 Python 封装类"""


    def __init__(self):
        # 通过 CoreFactory 获取 Assets 实例
        ...

    @staticmethod
    def read(path):
        """
        读取资产文件内容
        :param path: 资产路径
        :return: 文件内容字符串
        """
        return _assets_cls.read(path)

    @staticmethod
    def copy(path, destPath):
        """
        拷贝资产文件到目标位置
        :param path: 源资产路径
        :param destPath: 目标路径
        :return: 是否拷贝成功
        """
        return _assets_cls.copy(path, destPath)

    @staticmethod
    def isFolder(folderPath):
        """
        判断是否是文件夹
        :param folderPath: 文件夹路径
        :return: 布尔
        """
        return _assets_cls.isFolder(folderPath)

    @staticmethod
    def isFile(filePath):
        """
        判断是否是文件
        :param filePath: 文件路径
        :return: 布尔
        """
        return _assets_cls.isFile(filePath)
