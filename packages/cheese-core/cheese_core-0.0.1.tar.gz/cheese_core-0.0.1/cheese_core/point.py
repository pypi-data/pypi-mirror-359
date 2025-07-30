
from java import jclass


CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
_point_cls = CoreFactory.INSTANCE.getPoint()
class point:

    def __init__(self):
        # 从核心工厂获取 Point 接口实现实例
        ...
    @staticmethod
    def clickPoint( x: int, y: int) -> bool:
        """
        点击指定屏幕坐标
        """
        return _point_cls.clickPoint(x, y)
    @staticmethod
    def swipeToPoint( sx: int, sy: int, ex: int, ey: int, duration: int) -> bool:
        """
        从起点滑动到终点，持续时间ms
        """
        return _point_cls.swipeToPoint(sx, sy, ex, ey, duration)
    @staticmethod
    def longClickPoint( x: int, y: int) -> bool:
        """
        长按指定坐标
        """
        return _point_cls.longClickPoint(x, y)
    @staticmethod
    def touchDown( x: int, y: int) -> bool:
        """
        模拟触摸按下事件
        """
        return _point_cls.touchDown(x, y)
    @staticmethod
    def touchMove(x: int, y: int) -> bool:
        """
        模拟触摸移动事件
        """
        return _point_cls.touchMove(x, y)
    @staticmethod
    def touchUp() -> bool:
        """
        模拟触摸抬起事件
        """
        return _point_cls.touchUp()
    @staticmethod
    def gesture(duration: int, points) -> bool:
        """
        单指手势，points传Array<Pair<Int, Int>>，需要Java数组格式
        """
        return _point_cls.gesture(duration, points)
    @staticmethod
    def gestures( duration: int, points_array) -> bool:
        """
        多指手势，points_array传Array<Array<Pair<Int, Int>>>
        """
        return _point_cls.gestures(duration, points_array)
