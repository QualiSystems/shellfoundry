import codecs
import os
import unittest
import mock
import xml.etree.ElementTree as etree

from pyfakefs import fake_filesystem_unittest
from shellfoundry.utilities.python_depedencies_packager import PythonDependenciesPackager
from shellfoundry.utilities.shell_datamodel_merger import ShellDataModelMerger
from pyfakefs.fake_filesystem import FakeFilesystem


class TestPythonDepdenciesPackager(fake_filesystem_unittest.TestCase):

    def setUp(self):
        self.setUpPyfakefs()


    def test_calls_pip_to_download_dependencies(self):

        requirements_file = 'req/requirements.requirements_file'
        self.fs.CreateFile(requirements_file, contents="")

        with mock.patch('shellfoundry.utilities.python_depedencies_packager.pip') as mock_pip:
            # Act

            packager = PythonDependenciesPackager()
            packager.save_offline_dependencies(requirements_file, 'dst')
            mock_pip.main.assert_called_once()
            _,call_params ,_ = mock_pip.main.mock_calls[0]
            main_params = call_params[0]
            self.assertIn('download', main_params)
            self.assertIn('--requirement=req/requirements.requirements_file', main_params)
            self.assertIn('--dest=dst', main_params)


    def test_removed_old_files_before_running(self):
        requirements_file = 'req/requirements.requirements_file'
        self.fs.CreateFile(requirements_file, contents="")
        file = 'dst/test.txt'
        self.fs.CreateFile(file, contents="")
        nested_file = 'dst/nested/test.txt'
        self.fs.CreateFile(nested_file, contents="")

        with mock.patch('shellfoundry.utilities.python_depedencies_packager.pip') as mock_pip:
            # Act
            packager = PythonDependenciesPackager()
            packager.save_offline_dependencies(requirements_file, 'dst')

        self.assertFalse(os.path.exists(file))
        self.assertFalse(os.path.exists(nested_file))


    def test_does_nothing_if_requirements_file_does_not_exist(self):
        requirements_file = 'req/requirements.requirements_file'

        with mock.patch('shellfoundry.utilities.python_depedencies_packager.pip') as mock_pip:
            # Act
            packager = PythonDependenciesPackager()
            packager.save_offline_dependencies(requirements_file, 'dst')
        mock_pip.main.assert_not_called()


