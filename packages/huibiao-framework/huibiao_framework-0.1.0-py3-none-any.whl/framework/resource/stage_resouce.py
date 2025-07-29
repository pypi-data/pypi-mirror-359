import inspect
import os
from abc import ABC, abstractmethod
from typing import List, Type, TypeVar

from framework.resource.base_resource import Resource
from framework.resource.dir_resource import SimpleDirResource
from framework.resource.file_resource import SimpleFileResource
from framework.utils.annotation import frozen_attrs


class StageResource(Resource, ABC):
    @abstractmethod
    def list_inner_resources(self) -> List[Resource]:
        """
        获取内部资源对象
        """
        pass

    def is_completed(self) -> bool:
        return all(resource.is_completed() for resource in self.list_inner_resources())

    def progress(self) -> float:
        progress = 0
        for resource in self.list_inner_resources():
            if resource.is_completed():
                progress += resource.contribute_point
        return progress


F = TypeVar("F", bound=SimpleFileResource)

D = TypeVar("D", bound=SimpleDirResource)


@frozen_attrs("step_name", "step_dir")
class StepStageResource(StageResource):
    """
    步骤资源基类
    """

    def __init__(self, task_dir: str, step_name: str, contribute_point: float):
        super().__init__(contribute_point)
        self.step_name = step_name
        self.step_dir = os.path.join(task_dir, step_name)
        os.makedirs(self.step_dir, exist_ok=True)

    def list_inner_resources(self) -> List[Resource]:
        return [
            value
            for name, value in inspect.getmembers(self, inspect.isclass)
            if isinstance(value, Resource)
        ]

    def genFileResource(
        self, file_resource_cls: Type[F], name: str, contribute_point: float
    ) -> F:
        return file_resource_cls(
            path=os.path.join(self.step_dir, name), contribute_point=contribute_point
        )

    def genDirResource(
        self,
        file_resource_cls: Type[F],
        name: str,
        contribute_point: float,
        dir_resource_cls: Type[D] = SimpleDirResource,
    ) -> D:
        return dir_resource_cls(
            folder=os.path.join(self.step_dir, name),
            contribute_point=contribute_point,
            resource_cls=file_resource_cls,
        )


S = TypeVar("S", bound=StepStageResource)


@frozen_attrs("task_dir", "task_id")
class TaskStageResource(StageResource):
    """
    算法任务资源基类
    """

    def __init__(self, task_resource_dir: str, task_id: str):
        self.task_dir = os.path.join(task_resource_dir, task_id)
        self.task_id = task_id
        os.makedirs(self.task_dir, exist_ok=True)
        super().__init__(1.0)

    def list_inner_resources(self) -> List[StepStageResource]:
        return [
            value
            for name, value in inspect.getmembers(self, inspect.isclass)
            if isinstance(value, StepStageResource)
        ]
