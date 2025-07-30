"""
ADB API wrapper for Cheese Core
"""

from java import jclass

CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")

_adb_cls = CoreFactory.INSTANCE.getADB()
class adb:


    def __init__(self):
        ...
    @staticmethod
    def exec(command: str) -> str:
        """
        同步执行 adb shell 命令，等待返回字符串结果
        :param command: adb shell 命令字符串
        :return: 执行结果字符串
        """
        return _adb_cls.exec(command)
