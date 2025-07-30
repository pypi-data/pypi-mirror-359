"""
Zip API wrapper for Cheese Core
"""

from java import jclass

# 引入 CoreFactory，获取 Zip 实例
CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
_zip_cls = CoreFactory.INSTANCE.getZip()

class zip:


    def __init__(self):
        ...

    @staticmethod
    def compress(src_file_path: str, dest_file_path: str, password: str) -> bool:
        """
        压缩文件夹或文件为 zip，支持密码
        :param src_file_path: 源文件或文件夹路径
        :param dest_file_path: 目标 zip 文件路径
        :param password: 压缩密码
        :return: 是否成功
        """
        return _zip_cls.compress(src_file_path, dest_file_path, password)

    @staticmethod
    def decompress(zip_file_path: str, dest_file_path: str, password: str) -> bool:
        """
        解压带密码的 zip 文件
        :param zip_file_path: zip 文件路径
        :param dest_file_path: 解压目标路径
        :param password: 解压密码
        :return: 是否成功
        """
        return _zip_cls.decompress(zip_file_path, dest_file_path, password)
