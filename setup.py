#!/usr/bin/env python

from setuptools import find_packages, setup

with open("version.txt") as version_file:
    version_from_file = version_file.read().strip()

with open("requirements.txt") as f_required:
    required = f_required.read().splitlines()

with open("test_requirements.txt") as f_tests:
    required_for_tests = f_tests.read().splitlines()


def get_file_content(file_name):
    with open(file_name) as f:
        return f.read()


setup(
    name="shellfoundry",
    version=version_from_file,
    description="shellfoundry - Quali tool for creating, "
    "building and installing CloudShell shells",
    long_description=get_file_content("README.rst")
    + "\n\n"
    + get_file_content("HISTORY.rst"),
    long_description_content_type="text/markdown",
    author="Quali",
    author_email="info@quali.com",
    url="https://github.com/QualiSystems/shellfoundry",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={"shellfoundry": ["data/*.yml", "data/*.json"]},
    entry_points={"console_scripts": ["shellfoundry = shellfoundry.bootstrap:cli"]},
    include_package_data=True,
    install_requires=required,
    tests_require=required_for_tests,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords="shellfoundry sandbox cloud virtualization "
    "vcenter cmp cloudshell quali command-line cli",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: Apache Software License",
    ],
    python_requires=">=2.7",
    test_suite="tests",
)
