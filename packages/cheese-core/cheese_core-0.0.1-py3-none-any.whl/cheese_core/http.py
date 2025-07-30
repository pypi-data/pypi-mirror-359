"""
Http API wrapper for Cheese Core
"""

from java import jclass

# 引入 Cheese 核心工厂
CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")

class http:
    """Http 接口的 Python 封装类"""

    def __init__(self):
        # 通过 CoreFactory 获取 Http 实例
        self._http = CoreFactory.INSTANCE.createHttp()

    def builder(self):
        """
        获取 OkHttpUtils.Builder 对象
        """
        return self._http.builder()
