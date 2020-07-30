#!/usr/bin/env python
# encoding: utf-8

"""
Unit Test
New version number
Shellfoundry
Github release
"""

import os
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import xml.etree.ElementTree as ET
import yaml
from git import Repo
import pytest
import requests
import random
import glob
import fire

from ..commands.pack_command import PackCommandExecutor
from ..commands.install_command import InstallCommandExecutor
from ..commands.dist_command import DistCommandExecutor

from .. import __version__


def main(args=None):

    parser = ArgumentParser(description='Create new TG release',
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('-V', '--version', action='version', version=__version__)
    parser.add_argument('-t', '--test', help='Full testing', action='store_true')
    parser.add_argument('-r', '--release', help='New release number')
    parser.add_argument('-m', '--message',
                        help='Commit message / release description, default message == release, description == empty')
    parser.add_argument('-u', '--user', help='Github user name')
    parser.add_argument('-p', '--password', help='Github user password')
    # Use this for debug or emergency...
    parser.add_argument('--no-shellfoundry', dest='shellfoundry', action='store_false',
                        help='Do not run shellfoundry before release')
    parser.add_argument('--no-commit', dest='commit', action='store_false',
                        help='Do not commit, just create release')
    parser.set_defaults(test=False, release=False, shellfoundry=True, commit=True)
    parsed_args = parser.parse_args()

    if parsed_args.test:
        test_version()

    if parsed_args.release:
        release_version(parsed_args)


def release_version(parsed_args):
    """
    Write new version number
    Commit and push
    :todo: create new preview release on github
    """

    if os.path.exists('shell-definition.yaml'):
        # second gen
        with open('shell-definition.yaml', 'r') as f:
            shell_definition = yaml.safe_load(f)
        shell_definition['metadata']['template_version'] = parsed_args.release
        with open("shell-definition.yaml", 'w') as f:
            yaml.safe_dump(shell_definition, f, default_flow_style=False)
    else:
        # first gen
        with open('shell.yml', 'r') as f:
            shell = yaml.safe_load(f)
        shell['shell']['version'] = parsed_args.release
        with open("shell.yml", 'w') as f:
            yaml.safe_dump(shell, f, default_flow_style=False)
        with open("version.txt", 'w') as f:
            f.write(parsed_args.release)

    drivermetadata = ET.parse('src/drivermetadata.xml')
    driver = drivermetadata.getroot()
    driver.attrib['Version'] = parsed_args.release
    drivermetadata.write('src/drivermetadata.xml')

    if parsed_args.shellfoundry:
        PackCommandExecutor().pack()
        DistCommandExecutor().dist(enable_cs_repo=True)

    repo = Repo('.')
    if parsed_args.commit:
        message = 'version ' + parsed_args.release
        if parsed_args.message:
            message += ' - ' + parsed_args.message
        repo.git.add('.')
        repo.git.commit('-m {}'.format(message))
        repo.git.push()
        repo.git.push('.', 'development:master')
        repo.git.push('origin', 'master:master')

    create_release(parsed_args, repo)


def create_release(parsed_args, repo):

    api_url = 'https://api.github.com/'
    uploads_url = 'https://uploads.github.com/'
    url = repo.config_reader().get('remote "origin"', 'url')
    org_name = url.split('/')[3]
    repo_name = url.split('/')[-1].split('.')[0]

    data = '{"scopes": ["repo", "user"], "note": "testing' + str(random.randint(0, 1000)) + '"}'
    r = requests.post(api_url + 'authorizations', data=data, auth=(parsed_args.user, parsed_args.password))
    auth = r.json()

    tag_name = parsed_args.release + '-Preview'
    print('Create release ' + tag_name)
    headers = {'Authorization': 'token ' + str(auth['token'])}
    body = parsed_args.message if parsed_args.message else ''
    data = {'tag_name': tag_name, 'name': repo_name + ' ' + tag_name, 'body': body, 'prerelease': True}
    r = requests.post(api_url + 'repos/{}/{}/releases'.format(org_name, repo_name), headers=headers, json=data)
    rel = r.json()

    headers = {'Authorization': 'token ' + str(auth['token']),
               'Accept': 'application/vnd.github.manifold-preview',
               'Content-Type': 'application/zip'}
    for zip_file in glob.glob(os.path.join(os.getcwd(), 'dist', '*.zip')):
        params = {'name': os.path.basename(zip_file)}
        data = open(zip_file, 'rb').read()
        r = requests.post(uploads_url + 'repos/{}/{}/releases/{}/assets'.format(org_name, repo_name, rel['id']),
                          headers=headers, params=params, data=data)

    r = requests.delete(api_url + 'authorizations/' + str(auth['id']),
                        auth=(parsed_args.user, parsed_args.password))


def test_version():

    InstallCommandExecutor().install()

    shell_test = glob.glob('tests/*_shell.py')
    if shell_test:
        if pytest.main(shell_test) > 0:
            raise SystemExit


if __name__ == "__main__":
    sys.exit(main((sys.argv[1:])))
