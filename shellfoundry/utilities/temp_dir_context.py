from __future__ import annotations

import shutil
import tempfile

from attrs import define, field


@define
class TempDirContext:
    remove_dir_on_error: bool = True
    prefix: str = ""
    temp_dir: str = field(init=False, default=None)

    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp(prefix=self.prefix)
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_val or (exc_val and self.remove_dir_on_error):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
