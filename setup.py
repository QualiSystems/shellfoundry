#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


def get_file_content(file_name):
    with open(file_name) as f:
        return f.read()

exec(open('shellfoundry/version.py').read())

setup(
    name='shellfoundry',
    version=__version__,
    description="shellfoundry - Quali tool for creating, building and installing CloudShell shells",
    long_description=get_file_content('README.rst') + '\n\n' + get_file_content('HISTORY.rst'),
    author="Boris Modylevsky",
    author_email='borismod@gmail.com',
    url='https://github.com/QualiSystems/shellfoundry',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={'shellfoundry': ['data/*.yml', 'data/*.json']},
    entry_points={
        "console_scripts": ['shellfoundry = shellfoundry.bootstrap:cli']
    },
    include_package_data=True,
    install_requires=get_file_content('requirements.txt'),
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='shellfoundry sandbox cloud virtualization vcenter cmp cloudshell quali command-line cli',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: Apache Software License",
    ],
    test_suite='tests',
    tests_require=get_file_content('test_requirements.txt')
)
