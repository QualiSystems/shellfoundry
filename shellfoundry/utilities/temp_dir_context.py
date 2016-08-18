import tempfile
import shutil


class TempDirContext:

    def __init__(self, prefix =''):
        self.temp_dir = None
        self.prefix=prefix

    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp(prefix=self.prefix)
        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.temp_dir,ignore_errors=True)
