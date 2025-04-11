from __future__ import annotations

import os


def assert_file_exists(obj, file_path):
    obj.assertTrue(
        os.path.exists(file_path),
        msg=f"File/directory {file_path} does not exist",
    )
    obj.assertTrue(os.path.isfile(file_path), msg=f"File {file_path} does not exist")


def assert_file_does_not_exist(obj, file_path):
    obj.assertFalse(os.path.exists(file_path), msg=f"File/directory {file_path} exists")
