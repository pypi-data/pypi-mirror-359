

from java import jclass

# 引入 Cheese 核心工厂
CoreFactory = jclass("net.codeocean.cheese.core.CoreFactory")
_permissions_cls = CoreFactory.INSTANCE.getPermissions()
class permissions:
    """Permissions 接口的 Python 封装类"""

    def __init__(self):
        # 通过 CoreFactory 获取 Permissions 实例
        ...

    ACCESSIBILITY = _permissions_cls.getACCESSIBILITY()
    FLOATING = _permissions_cls.getFLOATING()
    RECORDSCREEN = _permissions_cls.getRECORDSCREEN()
    ROOT = _permissions_cls.getROOT()

    @staticmethod
    def requestPermission( permission: int, timeout: int) -> bool:
        """
        请求权限
        :param permission: 权限标识（整数）
        :param timeout: 超时时间（毫秒）
        :return: 是否成功请求权限
        """
        return _permissions_cls.requestPermission(permission, timeout)
    @staticmethod
    def checkPermission( permission: int) -> bool:
        """
        检查是否拥有指定权限
        :param permission: 权限标识（整数）
        :return: 是否拥有权限
        """
        return _permissions_cls.checkPermission(permission)
