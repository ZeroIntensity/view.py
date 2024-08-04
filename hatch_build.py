from hatchling.metadata.plugin.interface import MetadataHookInterface
import pyawaitable
import os

class JSONMetaDataHook(MetadataHookInterface):
    def update(self, *_) -> None:
        os.environ["PYAWAITABLE_INCLUDE_DIR"] = pyawaitable.include()
