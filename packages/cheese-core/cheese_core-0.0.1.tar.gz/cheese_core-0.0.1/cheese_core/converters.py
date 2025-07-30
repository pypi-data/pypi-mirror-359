"""
Converters API wrapper for Cheese Core
"""

from java import jclass

CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
_converters_cls = CoreFactory.INSTANCE.getConverters()

class converters:



    def __init__(self):
        ...

    @staticmethod
    def arrayToArrayList(object_list):
        """
        将列表转换成 Java 数组
        :param object_list: Python list[str]
        :return: Java array
        """
        return _converters_cls.arrayToArrayList(object_list)

    @staticmethod
    def pairArray(*elements: int):
        """
        构造 Pair<Int, Int> 数组
        :param elements: 可变参数，每两个构成一个 pair
        :return: Array<Pair<Int, Int>>
        """
        return _converters_cls.pairArray(*elements)

    @staticmethod
    def pairArrays(*arrays):
        """
        构造二维 Pair<Int, Int> 数组
        :param arrays: 每个元素为 Array<Pair<Int, Int>>
        :return: Array<Array<Pair<Int, Int>>>
        """
        return _converters_cls.pairArrays(*arrays)

    @staticmethod
    def sdToStream(file_path: str):
        """
        SD 卡路径文件转 InputStream
        """
        return _converters_cls.sdToStream(file_path)

    @staticmethod
    def assetsToStream(file_path: str):
        """
        Assets 文件转 InputStream
        """
        return _converters_cls.assetsToStream(file_path)

    @staticmethod
    def assetsToBitmap(file_path: str):
        """
        Assets 文件转 Bitmap
        """
        return _converters_cls.assetsToBitmap(file_path)

    @staticmethod
    def streamToBitmap(input_stream):
        """
        InputStream 转 Bitmap
        """
        return _converters_cls.streamToBitmap(input_stream)

    @staticmethod
    def bitmapToStream(bitmap):
        """
        Bitmap 转 InputStream
        """
        return _converters_cls.bitmapToStream(bitmap)

    @staticmethod
    def base64ToBitmap(base64_string: str):
        """
        Base64 字符串转 Bitmap
        """
        return _converters_cls.base64ToBitmap(base64_string)

    @staticmethod
    def bitmapToBase64(bitmap):
        """
        Bitmap 转 Base64 字符串
        """
        return _converters_cls.bitmapToBase64(bitmap)
