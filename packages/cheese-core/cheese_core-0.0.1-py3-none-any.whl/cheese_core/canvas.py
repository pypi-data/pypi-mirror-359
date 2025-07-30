"""
Canvas API wrapper for Cheese Core
"""

from java import jclass
from typing import overload  # Python 3.5+

# 引入 Cheese 核心工厂
CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
_canvas_cls = CoreFactory.INSTANCE.getCanvas()

class canvas:
    """
    Canvas 接口的 Python 封装类
    """


    def __init__(self):
        ...

    @staticmethod
    @overload
    def drawRectOnScreen(similarityText: str, rect: 'Rect') -> 'EasyWindow':
        ...

    @staticmethod
    @overload
    def drawRectOnScreen(textColor: int, borderedColor: int, similarityText: str, rect: 'Rect') -> 'EasyWindow':
        ...

    @staticmethod
    def drawRectOnScreen(*elements) -> 'EasyWindow':
        """
        在屏幕上绘制矩形
        有两种调用方式:
        1. textColor (int), borderedColor (int), similarityText (str), Rect 对象
        2. similarityText (str), Rect 对象

        :return: EasyWindow 实例
        """
        return _canvas_cls.drawRectOnScreen(list(elements))

    @staticmethod
    @overload
    def drawPointOnScreen(

            textColor: int,
            pointColor: int,
            similarityText: str,
            x: float,
            y: float
    ) -> 'EasyWindow':
        ...

    @staticmethod
    @overload
    def drawPointOnScreen(

            similarityText: str,
            x: float,
            y: float
    ) -> 'EasyWindow':
        ...

    @staticmethod
    def drawPointOnScreen(*elements) -> 'EasyWindow':
        return _canvas_cls.drawPointOnScreen(list(elements))
