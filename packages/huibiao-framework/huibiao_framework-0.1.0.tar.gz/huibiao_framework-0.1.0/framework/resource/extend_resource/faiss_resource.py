from framework.resource.file_resource import SimpleFileResource
import faiss


class FaissIndexResource(SimpleFileResource[faiss.Index]):
    @classmethod
    def file_suffix(cls):
        return ".index"

    def load(self):
        self.setData(faiss.read_index(self.resource_path))

    def save(self):
        faiss.write_index(self.getData(), self.resource_path)
