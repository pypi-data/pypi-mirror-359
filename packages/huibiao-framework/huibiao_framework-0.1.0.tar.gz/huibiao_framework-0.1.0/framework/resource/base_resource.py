from abc import ABC, abstractmethod

from framework.utils.constant import ConstantClass
from framework.utils.annotation import frozen_attrs


class ResourceStatusTagConstant(ConstantClass):
    DONE = "__DONE"


@frozen_attrs("contribute_point ")
class Resource(ABC):
    def __init__(self, contribute_point: float):
        self.contribute_point = contribute_point

    @abstractmethod
    def is_completed(self, *args, **kwargs) -> bool:
        """
        该资源是否准备完毕
        """
        pass
