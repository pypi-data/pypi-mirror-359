import os
from pathlib import Path
from typing import Self

from pydantic import BaseModel

from bmhub.utils import format_size, format_timesince

FILES_TO_IGNORE: list[str] = [".DS_Store"]


class ModelInfo(BaseModel):
    id: str
    path: Path
    size_on_disk: int
    num_files: int
    last_accessed_timestamp: float
    last_modified_timestamp: float

    @property
    def last_accessed_str(self) -> str:
        return format_timesince(timestamp=self.last_accessed_timestamp)

    @property
    def last_modified_str(self) -> str:
        return format_timesince(timestamp=self.last_modified_timestamp)

    @property
    def size_on_disk_str(self) -> str:
        return format_size(size=self.size_on_disk)

    @classmethod
    def from_local_path(cls, *, model_path: Path) -> Self:
        model_id: str = f"{model_path.parent.name}/{model_path.name}"
        size_on_disk: int = 0
        num_files: int = 0
        last_accessed_timestamp: float = 0
        last_modified_timestamp: float = 0
        for file_path in model_path.glob(pattern="**/*"):
            if not file_path.is_file():
                continue
            if file_path.name in FILES_TO_IGNORE:
                continue
            file_stats: os.stat_result = file_path.stat()
            size_on_disk += file_stats.st_size
            num_files += 1
            last_accessed_timestamp = max(last_accessed_timestamp, file_stats.st_atime)
            last_modified_timestamp = max(last_modified_timestamp, file_stats.st_mtime)
        if num_files == 0:
            model_stats: os.stat_result = model_path.stat()
            last_accessed_timestamp = model_stats.st_atime
            last_modified_timestamp = model_stats.st_mtime
        return cls(
            id=model_id,
            path=model_path,
            size_on_disk=size_on_disk,
            num_files=num_files,
            last_accessed_timestamp=last_accessed_timestamp,
            last_modified_timestamp=last_modified_timestamp,
        )
