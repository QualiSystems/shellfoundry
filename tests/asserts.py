import os


def assertFileExists(obj, file_path):
    obj.assertTrue(os.path.exists(file_path), msg='File/directory {0} does not exist'.format(file_path))
    obj.assertTrue(os.path.isfile(file_path), msg='File {0} does not exist'.format(file_path))


def assertFileDoesNotExist(obj, file_path):
    obj.assertFalse(os.path.exists(file_path), msg='File/directory {0} exists'.format(file_path))
