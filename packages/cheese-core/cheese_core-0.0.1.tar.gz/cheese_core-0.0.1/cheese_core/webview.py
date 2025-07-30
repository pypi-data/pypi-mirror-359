"""
WebView API wrapper for Cheese Core
"""

from java import jclass
from java import dynamic_proxy
CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
from net.codeocean.cheese.core import IAction # type: ignore
_webview_cls = CoreFactory.INSTANCE.getWebView()
class webview:


    def __init__(self):
        ...
    @staticmethod
    def ui(iwebview):
        class UI(dynamic_proxy(IAction)):
            def invoke(self,e):
               return iwebview(e)

        _webview_cls.inject(UI())
    @staticmethod
    def run_webview(id: str):
        _webview_cls.runWebView(id)
    @staticmethod
    def document(method_name: str, *args):
        """
        调用 document 下的 JS 方法或属性
        :param method_name: 方法名或属性名（可带括号）
        :param args: 参数列表
        :return: JS 执行返回的结果（同步等待）
        """
        # 传递给 Kotlin 的接口会同步等待执行结果
        return _webview_cls.document(method_name, *args)
    @staticmethod
    def window(method_name: str, *args):
        """
        调用 window 下的 JS 方法或属性
        :param method_name: 方法名或属性名（可带括号）
        :param args: 参数列表
        :return: JS 执行返回的结果（同步等待）
        """
        return _webview_cls.window(method_name, *args)
