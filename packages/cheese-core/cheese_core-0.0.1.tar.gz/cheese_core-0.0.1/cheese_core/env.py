"""
Env 接口的 Python 封装
"""

from java import jclass


CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
_env_cls = CoreFactory.INSTANCE.getEnv()

class env:



    def __init__(self):
        ...
    @staticmethod
    @property
    def context():
        """
        返回 Context
        """
        return _env_cls.getContext()
    @staticmethod
    @property
    def version() -> str:
        """
        版本
        """
        return _env_cls.getVersion()
    @staticmethod
    @property
    def settings():
        """
        返回可变设置 (Map)
        """
        return _env_cls.getSettings()
    @staticmethod
    @property
    def activity():
        """
        当前 Activity
        """
        return _env_cls.getActivity()
