
from java import jclass
from typing import TypedDict
# 引入 Cheese 核心工厂
CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
class File(TypedDict):
    path: str

_uinode_cls =  CoreFactory.INSTANCE.getPath()
class path:

    """Path 接口的 Python 封装类"""

    def __init__(self):
        ...

    @staticmethod
    @property
    def ROOT_DIRECTORY() -> File:
        """
        获取根目录 File 对象
        :return: java.io.File
        """
        return _uinode_cls._path.ROOT_DIRECTORY

    @staticmethod
    @property
    def WORKING_DIRECTORY() -> File:
        """
        获取根目录 File 对象
        :return: java.io.File
        """
        return _uinode_cls._path.WORKING_DIRECTORY

    @staticmethod
    @property
    def LOG_DIRECTORY() -> File:
        """
        获取根目录 File 对象
        :return: java.io.File
        """
        return _uinode_cls._path.LOG_DIRECTORY

    @staticmethod
    @property
    def MAIN_DIRECTORY() -> File:
        """
        获取根目录 File 对象
        :return: java.io.File
        """
        return _uinode_cls._path.MAIN_DIRECTORY

    @staticmethod
    @property
    def UI_DIRECTORY() -> File:
        """
        获取根目录 File 对象
        :return: java.io.File
        """
        return _uinode_cls._path.UI_DIRECTORY


    @staticmethod
    @property
    def ASSETS_DIRECTORY() -> File:
        """
        获取根目录 File 对象
        :return: java.io.File
        """
        return _uinode_cls._path.ASSETS_DIRECTORY

    @staticmethod
    @property
    def JS_DIRECTORY() -> File:
        """
        获取根目录 File 对象
        :return: java.io.File
        """
        return _uinode_cls._path.JS_DIRECTORY
