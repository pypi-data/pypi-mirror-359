
from java import jclass

# 引入 Cheese 核心工厂
CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
_keyboard_cls = CoreFactory.INSTANCE.getKeyboard()

class keyboard:
    """Keyboard 接口的 Python 封装类"""


    def __init__(self):
        # 通过 CoreFactory 获取 Keyboard 实例
        ...

    @staticmethod
    def input(text: str):
        """
        输入文本
        :param text: 要输入的字符串
        """
        _keyboard_cls.input(text)

    @staticmethod
    def delete():
        """
        删除当前输入内容（尽量删除所有）
        """
        _keyboard_cls.delete()

    @staticmethod
    def enter():
        """
        模拟回车键输入
        """
        _keyboard_cls.enter()
