
from java import jclass

# 引入 Cheese 核心工厂
CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
from typing import Protocol, List, Any, runtime_checkable


@runtime_checkable
class PaddleOcrv5(Protocol):


    def ocr(self, image: 'Bitmap') -> str:
        """执行OCR识别
        Args:
            image: 输入的Android Bitmap对象
        Returns:
            识别结果字符串
        """
        ...

    def init(self) -> bool:
        """初始化OCR引擎
        Returns:
            初始化是否成功
        """
        ...

@runtime_checkable
class PaddleOcrv4(Protocol):
    """对应PaddleOcrv4的Python Protocol定义"""

    def ocr(self, image: 'Bitmap') -> List['PaddleOcrNcnn']:
        """执行OCR识别并返回结果列表
        Args:
            image: 输入的Android Bitmap对象
        Returns:
            PaddleOcrNcnn对象列表，每个元素包含识别结果
        """
        ...

    def init(self, path: str) -> bool:
        """初始化OCR引擎
        Args:
            path: 模型路径（如assets目录路径）
        Returns:
            初始化是否成功
        """
        ...

@runtime_checkable
class Text(Protocol):
    """对应TypeScript的Text类型定义"""

    class Result(Protocol):
        class TextBlocks(Protocol):
            class TextBlock(Protocol):
                class Line(Protocol):
                    def size(self) -> int: ...
                    def get(self, index: int) -> Any: ...

                class BoundingBox(Protocol):
                    left: int
                    top: int
                    right: int
                    bottom: int
                    def width(self) -> int: ...
                    def height(self) -> int: ...

                def getText(self) -> str: ...
                def getLines(self) -> Line: ...
                def getBoundingBox(self) -> BoundingBox: ...
                def getCornerPoints(self) -> List['Point']: ...
                def getRecognizedLanguage(self) -> str: ...

            def size(self) -> int: ...
            def get(self, index: int) -> TextBlock: ...

        def getTextBlocks(self) -> TextBlocks: ...
        def getText(self) -> str: ...

    result: Result

_ocr_cls = CoreFactory.INSTANCE.getOCR()

class ocr:
    """OCR 接口的 Python 封装类"""

    CHINESE = 1
    LATIN = 2

    def __init__(self):
        # 通过 CoreFactory 获取 OCR 实例
        ...
    @staticmethod
    def mlkitOcr( bitmap: 'Bitmap', recognizer: int) ->Text:
        """
        使用 MLKit 进行文字识别
        :param bitmap: android.graphics.Bitmap 对象
        :param recognizer: 识别类型，CHINESE 或 LATIN
        :return: MlkitCore.ResultType 或 None
        """
        return _ocr_cls.mlkitOcr(bitmap, recognizer)
    @staticmethod
    def paddleOcrv4() ->PaddleOcrv4:
        """
        获取 PaddleOCR v4 处理器实例
        :return: PaddleOCRHandler 对象
        """
        return _ocr_cls.paddleOcrv4()
    @staticmethod
    def paddleOcrv5() ->PaddleOcrv5:
        """
        获取 PaddleOCR v5 处理器实例
        :return: PPOCR 对象
        """
        return _ocr_cls.paddleOcrv5()


