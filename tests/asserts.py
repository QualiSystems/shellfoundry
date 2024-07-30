#!/usr/bin/python
import os


def assertFileExists(obj, file_path):
    obj.assertTrue(
        os.path.exists(file_path),
        msg=f"File/directory {file_path} does not exist",
    )
    obj.assertTrue(os.path.isfile(file_path), msg=f"File {file_path} does not exist")


def assertFileDoesNotExist(obj, file_path):
    obj.assertFalse(os.path.exists(file_path), msg=f"File/directory {file_path} exists")
