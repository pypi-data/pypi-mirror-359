import os
import time
from typing import Generic, List, Type, TypeVar, final

from framework.resource.base_resource import ResourceStatusTagConstant
from framework.resource.file_resource import FileResource, SimpleFileResource
from framework.utils.annotation import frozen_attrs

F = TypeVar("F", bound=SimpleFileResource)


@frozen_attrs("folder")
class SimpleDirResource(Generic[F], FileResource):
    """
    相同资源的文件构成的目录
    """

    def __init__(
        self,
        folder: str,
        resource_cls: Type[F] = SimpleFileResource,
        contribute_point: float = 0,
    ):
        self.folder = folder
        os.makedirs(self.folder, exist_ok=True)
        super().__init__(contribute_point)
        self._resource_cls: Type[F] = resource_cls
        self._resources: List[F] = [self._resource_cls(f) for f in self.resource_path]

    @final
    def set_completed(self):
        with open(
            os.path.join(self.folder, ResourceStatusTagConstant.DONE),
            "w",
        ) as f:
            local_time = time.localtime(time.time())
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
            f.write(formatted_time)  # 往目录下写入一个文件，包含当前时间

    @final
    def is_completed(self) -> bool:
        return os.path.exists(os.path.join(self.folder, ResourceStatusTagConstant.DONE))

    def genAppendPath(self):
        return os.path.join(
            self.folder, f"{len(self._resources)}{self._resource_cls.file_suffix()}"
        )

    def appendSave(self, data, **kwargs) -> F:
        if self.is_completed():
            raise Exception("已收集完毕，无法添加新的资源文件")
        new_resource_item: Type[F] = self._resource_cls(path=self.genAppendPath())
        new_resource_item.setData(data)
        new_resource_item.save(**kwargs)
        self._resources.append(new_resource_item)
        return new_resource_item

    @final
    @property
    def resource_path(self) -> List[str]:
        return [
            os.path.join(self.folder, f)
            for f in os.listdir(self.folder)
            if f != ResourceStatusTagConstant.DONE
        ]

    def load(self, **kwargs):
        for r in self._resources:
            r.load(**kwargs)

    def __getitem__(self, idx) -> F:
        return self._resources[idx]

    def __len__(self):
        return len(self._resources)
