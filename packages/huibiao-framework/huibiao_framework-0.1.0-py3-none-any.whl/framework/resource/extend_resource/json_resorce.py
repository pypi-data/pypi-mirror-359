import json
from typing import Dict

from framework.resource.file_resource import SimpleFileResource


class JsonFileResource(SimpleFileResource[Dict]):
    @classmethod
    def file_suffix(cls):
        return ".json"

    def load(self):
        with open(self.resource_path, "r", encoding="utf-8") as f:
            self.setData(json.load(f))

    def save(self):
        with open(self.resource_path, "w", encoding="utf-8") as f:
            json.dump(self.getData(), f, ensure_ascii=False, indent=2)
