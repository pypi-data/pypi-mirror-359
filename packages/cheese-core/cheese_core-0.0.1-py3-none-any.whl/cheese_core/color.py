

from java import jclass

CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
_color_cls = CoreFactory.INSTANCE.getColor()

class color:
    """
    Color 接口的 Python 封装
    """


    def __init__(self):
        ...

    @staticmethod
    def compareColor(baseColorHex: str, targetColorHex: str, options: dict) -> bool:
        """
        比较两个颜色是否相似
        :param baseColorHex: 基准颜色（如 #FF0000）
        :param targetColorHex: 目标颜色
        :param options: dict, 例如
           {
             "maxDistance": 0.15,
             "hueWeight": 0.7,
             "saturationWeight": 0.2,
             "valueWeight": 0.1,
             "considerAlpha": True
           }
        :return: 是否相似
        """
        return _color_cls.compareColor(baseColorHex, targetColorHex, options)

    @staticmethod
    def getPointColor(inputImage, format: int, x: int, y: int):
        """
        获取图片指定坐标的颜色数组
        :param inputImage: Bitmap
        :param format: 0=RGB, 1=ARGB
        :param x: 横坐标
        :param y: 纵坐标
        :return: [r, g, b] 或 [a, r, g, b]
        """
        return _color_cls.getPointColor(inputImage, format, x, y)

    @staticmethod
    def getPointHEX(inputImage, format: int, x: int, y: int) -> str:
        """
        获取指定坐标的16进制颜色
        """
        return _color_cls.getPointHEX(inputImage, format, x, y)

    @staticmethod
    def rgbToHEX(r: int, g: int, b: int) -> str:
        """
        RGB转HEX
        """
        return _color_cls.rgbToHEX(r, g, b)

    @staticmethod
    def argbToHEX(a: int, r: int, g: int, b: int) -> str:
        """
        ARGB转HEX
        """
        return _color_cls.argbToHEX(a, r, g, b)

    @staticmethod
    def parseHex(hex: str):
        """
        解析HEX字符串
        :return: [r,g,b] 或 [a,r,g,b]
        """
        return _color_cls.parseHex(hex)

    @staticmethod
    def parseColor(colorString: str):
        """
        解析颜色字符串
        :return: int
        """
        return _color_cls.parseColor(colorString)

    @staticmethod
    def findMultiColors(bitmap, firstColor: str, paths: list, options: dict):
        """
        多点路径颜色搜索
        :param bitmap: Bitmap
        :param firstColor: 首个颜色
        :param paths: [[x,y,color], ...]
        :param options: dict
        """
        return _color_cls.findMultiColors(bitmap, firstColor, paths, options)
