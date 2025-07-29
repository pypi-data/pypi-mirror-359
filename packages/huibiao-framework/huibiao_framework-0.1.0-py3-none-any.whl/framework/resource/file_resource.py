import os
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, final

from framework.resource.base_resource import Resource


class FileResource(Resource, ABC):
    """
    文件资源
    """

    @abstractmethod
    def resource_path(self):
        pass

    @abstractmethod
    def load(self, **kwargs):
        """
        从本地加载
        """
        pass


T = TypeVar("T")


class SimpleFileResource(Generic[T], FileResource):
    """
    单个文件
    """

    def __init__(self, path: str, contribute_point: float = 0):
        if not path.endswith(self.file_suffix()):
            raise Exception(f"文件{path}后缀错误，后缀必须是{self.file_suffix()}")
        self._path = path
        super().__init__(contribute_point)
        self.__data: T = None

    def is_completed(self) -> bool:
        return os.path.exists(self._path)

    @final
    @property
    def resource_path(self) -> str:
        return self._path

    def getData(self) -> T:
        return self.__data

    def loadAndGet(self, **kwargs) -> T:
        self.load(**kwargs)
        return self.getData()

    def setData(self, data: T):
        self.__data = data

    @abstractmethod
    def save(self, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def file_suffix(cls):
        """子类必须实现此类方法"""
        pass
