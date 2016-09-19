import tempfile
import shutil


class TempDirContext:
    def __init__(self, remove_dir_on_error=True, prefix=''):
        self.temp_dir = None
        self.prefix = prefix
        self._remove_dir_on_error = remove_dir_on_error

    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp(prefix=self.prefix)
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_val or (exc_val and self._remove_dir_on_error):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

