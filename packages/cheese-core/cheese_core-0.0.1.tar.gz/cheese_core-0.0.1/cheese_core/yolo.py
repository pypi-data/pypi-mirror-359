"""
Yolo API wrapper for Cheese Core
"""

from java import jclass

# 引入 CoreFactory，获取 Yolo 接口实例
CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")

_yolo_cls = CoreFactory.INSTANCE.getYolo()
class yolo:

    def __init__(self):
        ...
    @staticmethod
    def detect(bitmap, path, labels_list, cpugpu):
        """
        调用 Yolo 的 detect 方法进行目标检测
        :param bitmap: Android Bitmap 对象
        :param path: 模型路径字符串
        :param labels_list: 字符串列表，模型类别标签
        :param cpugpu: int，选择 CPU(0) 或 GPU(1)
        :return: Yolov8Ncnn.Obj[] 数组
        """
        # Kotlin 层要求 ArrayList<Any>，这里将列表传递给 Kotlin 层会自动转换
        # labels_list 必须是字符串列表
        return _yolo_cls.detect(bitmap, path, labels_list, cpugpu)
    @staticmethod
    def get_speed():
        """
        获取检测速度，单位秒
        :return: float
        """
        return _yolo_cls.getSpeed()
    @staticmethod
    def draw(objects, bitmap):
        """
        在 bitmap 上绘制检测结果
        :param objects: Yolov8Ncnn.Obj[] 数组
        :param bitmap: Android Bitmap
        :return: Bitmap，绘制后图像
        """
        return _yolo_cls.draw(objects, bitmap)
