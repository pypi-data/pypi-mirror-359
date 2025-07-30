"""
Files API wrapper for Cheese Core
"""

from java import jclass

# 引入 Cheese 核心工厂
CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
_files_cls = CoreFactory.INSTANCE.getFiles()

class files:


    def __init__(self):
        ...
    @staticmethod
    def read( path: str):
        """
        读取文件内容，返回字符串数组
        """
        return _files_cls.read(path)
    @staticmethod
    def rm( path: str) -> bool:
        """
        删除文件或目录
        """
        return _files_cls.rm(path)
    @staticmethod
    def create( path: str) -> bool:
        """
        创建文件或目录
        """
        return _files_cls.create(path)
    @staticmethod
    def copy( source_dir_path: str, destination_dir_path: str) -> bool:
        """
        复制文件或目录
        """
        return _files_cls.copy(source_dir_path, destination_dir_path)
    @staticmethod
    def readJson( file_path: str, keys: str):
        """
        读取 JSON 文件中指定 key 的内容
        """
        return _files_cls.readJson(file_path, keys)
    @staticmethod
    def isFile( path: str) -> bool:
        """
        判断路径是否是文件
        """
        return _files_cls.isFile(path)
    @staticmethod
    def isFolder( path: str) -> bool:
        """
        判断路径是否是目录
        """
        return _files_cls.isFolder(path)
    @staticmethod
    def append( file_path: str, content: str) -> bool:
        """
        追加内容到文件末尾
        """
        return _files_cls.append(file_path, content)
    @staticmethod
    def write( file_path: str, content: str) -> bool:
        """
        覆盖写入文件内容
        """
        return _files_cls.write(file_path, content)
    @staticmethod
    def save( obj, file_path: str) -> bool:
        """
        将对象保存到文件（序列化）
        """
        return _files_cls.save(obj, file_path)
