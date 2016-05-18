import os


def assertFileExists(obj, file_path):
    obj.assertTrue(os.path.exists(file_path), msg='File {0} does not exist'.format(file_path))
