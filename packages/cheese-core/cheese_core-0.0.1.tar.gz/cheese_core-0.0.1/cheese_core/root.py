"""
Root API wrapper for Cheese Core
"""

from java import jclass

CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
_root_cls = CoreFactory.INSTANCE.getRoot()

class root:


    def __init__(self):
        ...
    @staticmethod
    def exec(command: str) -> str:
        """
        执行 su 权限命令并返回结果字符串
        :param command: 要执行的命令字符串
        :return: 命令执行结果
        """
        return _root_cls.exec(command)
    @staticmethod
    def request_permission(timeout: int) -> bool:
        """
        请求 Root 权限
        :param timeout: 超时时间
        :return: 是否请求成功
        """
        return _root_cls.requestPermission(timeout)
    @staticmethod
    def check_permission() -> bool:
        """
        检查是否有 Root 权限
        :return: 是否有权限
        """
        return _root_cls.checkPermission()
