#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from shellfoundry.decorators import list_presentation
from shellfoundry.commands.install_command import InstallCommandExecutor
from shellfoundry.commands.list_command import ListCommandExecutor
from shellfoundry.commands.new_command import NewCommandExecutor
from shellfoundry.commands.pack_command import PackCommandExecutor
from shellfoundry.commands.config_command import ConfigCommandExecutor


@list_presentation.to_json
def templates_list():
    """ Lists the available shell templates """

    return ListCommandExecutor().list()


def new_shell(name, template, extra_content, path):
    """ Creates a new shell based on a template """

    os.chdir(path)
    return NewCommandExecutor().new(name=name, template=template, extra_context=extra_content)


def install_shell(shell_path):
    """ Installs the shell package into CloudShell """

    os.chdir(shell_path)
    PackCommandExecutor().pack()
    InstallCommandExecutor().install()


if __name__ == "__main__":
    # print templates_list()
    print new_shell(name="test cs 1",
                    template="gen2/networking/router",
                    extra_content="",
                    path="D:\cs_shellfoundry")
    # install_shell("D:\cs_shellfoundry\\test_cs")
