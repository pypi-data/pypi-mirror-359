"""
Thread API wrapper for Cheese Core
"""

from java import jclass

CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
from typing import Protocol

class Thread(Protocol):
    def exit(self) -> None: ...
    def get_id(self) -> str: ...

class thread:

    def __init__(self):
        self._thread = CoreFactory.INSTANCE.createThread()

    def create(self, runnable) ->Thread:
        """
        创建线程并提交 runnable
        :param runnable: Java Runnable 对象
        :return: self
        """
        return self._thread.create(runnable)


