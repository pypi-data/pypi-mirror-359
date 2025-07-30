"""
Image API wrapper for Cheese Core
"""

from java import jclass

# 引入 Cheese 核心工厂
CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")

_image_cls = CoreFactory.INSTANCE.getImage()
class image:
    """Image 接口的 Python 封装类"""


    def __init__(self):
        # 通过 CoreFactory 获取 Image 实例
        ...
    @staticmethod
    def drawRectOnBitmap(*elements):
        """
        在 Bitmap 上绘制矩形框及文字，参数灵活：
        - 5个参数：bitmap, text, textColor, borderedColor, rect
        - 3个参数：bitmap, text, rect（颜色默认）
        """
        return _image_cls.drawRectOnBitmap(*elements)
    @staticmethod
    def drawPointOnBitmap(*elements):
        """
        在 Bitmap 上绘制点及文字，参数灵活：
        - 6个参数：bitmap, text, textColor, pointColor, x, y
        - 4个参数：bitmap, text, x, y（颜色默认）
        """
        return _image_cls.drawPointOnBitmap(*elements)
    @staticmethod
    def showBitmapView(bitmap):
        """
        在界面上展示 Bitmap
        """
        _image_cls.showBitmapView(bitmap)
    @staticmethod
    def release(bitmap):
        """
        回收 Bitmap 资源
        """
        _image_cls.release(bitmap)
    @staticmethod
    def decodeQRCode(bitmap):
        """
        解析 Bitmap 中的二维码，返回字符串内容
        """
        return _image_cls.decodeQRCode(bitmap)
    @staticmethod
    def read(path):
        """
        从文件路径读取 Bitmap
        """
        return _image_cls.read(path)
    @staticmethod
    def clip(bitmap, left, top, right, bottom):
        """
        裁剪 Bitmap，返回裁剪后的 Bitmap
        """
        return _image_cls.clip(bitmap, left, top, right, bottom)
    @staticmethod
    def generateQRCode(content, width, height):
        """
        生成二维码 Bitmap
        """
        return _image_cls.generateQRCode(content, width, height)
    @staticmethod
    def drawJsonBoundingBoxes(bitmap, jsonStr):
        """
        根据 JSON 字符串绘制边框和文字
        """
        return _image_cls.drawJsonBoundingBoxes(bitmap, jsonStr)
    @staticmethod
    def findImgBySift(inputImage, targetImage, maxDistance):
        """
        使用 SIFT 算法匹配图像位置
        """
        return _image_cls.findImgBySift(inputImage, targetImage, maxDistance)
    @staticmethod
    def findImgByTemplate(inputImage, targetImage, similarityThreshold):
        """
        使用模板匹配算法查找目标图像位置
        """
        return _image_cls.findImgByTemplate(inputImage, targetImage, similarityThreshold)
    @staticmethod
    def findImgByResize(inputImage, targetImage, similarityThreshold, width, height):
        """
        缩放大图后模板匹配，返回中心点及置信度
        """
        return _image_cls.findImgByResize(inputImage, targetImage, similarityThreshold, width, height)
    @staticmethod
    def fastFindImg(inputImage, targetImage, similarityThreshold):
        """
        快速模板匹配查找图像位置
        """
        return _image_cls.fastFindImg(inputImage, targetImage, similarityThreshold)
    @staticmethod
    def resize(inputBitmap, scale):
        """
        按比例缩放 Bitmap
        """
        return _image_cls.resize(inputBitmap, scale)
    @staticmethod
    def binarize(inputBitmap, threshold):
        """
        二值化处理 Bitmap
        """
        return _image_cls.binarize(inputBitmap, threshold)
