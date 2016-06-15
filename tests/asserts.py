import os


def assertFileExists(obj, file_path):
    obj.assertTrue(os.path.exists(file_path), msg='File {0} does not exist'.format(file_path))

def assertFileNotExists(obj, file_path):
    obj.assertTrue(not os.path.exists(file_path), msg='File {0} should not exist'.format(file_path))
