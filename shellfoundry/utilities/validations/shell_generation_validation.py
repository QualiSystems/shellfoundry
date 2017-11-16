#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import zipfile

from shellfoundry.utilities.constants import TOSCA_META_LOCATION


class ShellGenerationValidations(object):

    def validate_2nd_gen(self, shell_path):
        """ Validate generation of Shell
            :param str shell_path: path to Shell directory or Shell zip-file
        """

        if os.path.isdir(shell_path):
            file_list = []
            for root, dirs, files in os.walk(shell_path):
                root = root.replace(shell_path, "").lstrip("\\").lstrip("/")
                for name in files:
                    file_list.append(os.path.join(root, name))

            if TOSCA_META_LOCATION in file_list:
                return True
            return False
        elif zipfile.is_zipfile(shell_path):
            raise NotImplemented
        else:
            raise Exception("Unexpected shell path type")
