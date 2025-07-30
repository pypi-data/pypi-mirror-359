
from java import jclass

# 引入 Cheese 核心工厂
CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")

_base_cls = CoreFactory.INSTANCE.getBase()
class base:
    """Base 接口的 Python 封装类"""


    def __init__(self):
        # 通过 CoreFactory 获取 Base 实例
        ...

    @staticmethod
    def sleep(millis):
        """
        线程休眠
        :param millis: 毫秒
        """
        _base_cls.sleep(millis)

    @staticmethod
    def exit():
        """
        退出脚本
        """
        _base_cls.exit()

    @staticmethod
    def runOnUi(action):
        """
        在 UI 线程运行
        :param action: IAction 实现
        """
        _base_cls.runOnUi(action)

    @staticmethod
    def release(resource):
        """
        释放资源
        :param resource: 任意 Java 对象
        :return: 是否释放成功
        """
        return _base_cls.release(resource)

    @staticmethod
    def Rect(left, top, right, bottom):
        """
        创建 Rect 对象
        """
        return _base_cls.Rect(left, top, right, bottom)

    @staticmethod
    def toast(message, gravity=None, xOffset=None, yOffset=None):
        """
        弹出 Toast 消息
        :param message: 消息文本
        :param gravity: 可选，位置
        :param xOffset: 可选，水平偏移
        :param yOffset: 可选，垂直偏移
        """
        if gravity is not None and xOffset is not None and yOffset is not None:
            _base_cls.toast(message, gravity, xOffset, yOffset)
        else:
            _base_cls.toast(message)
