
from java import jclass

# 引入 Cheese 核心工厂
CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")

_persistentstore_cls = CoreFactory.INSTANCE.getPersistentStore()
class persistentstore:


    """PersistentStore 接口的 Python 封装类"""

    def __init__(self):
        # 通过 CoreFactory 获取 PersistentStore 实例
        ...
    @staticmethod
    def save( name: str, key: str, value):
        """
        保存数据到持久化存储
        :param name: 存储名称（SharedPreferences 名称）
        :param key: 键
        :param value: 值（支持 String, Int, Boolean, ByteArray）
        """
        _persistentstore_cls.save(name, key, value)
    @staticmethod
    def rm(name: str, key: str):
        """
        删除指定键的数据
        :param name: 存储名称
        :param key: 键
        """
        _persistentstore_cls.rm(name, key)
    @staticmethod
    def get( name: str, key: str):
        """
        获取指定键对应的数据
        :param name: 存储名称
        :param key: 键
        :return: 值或 None
        """
        return _persistentstore_cls.get(name, key)
