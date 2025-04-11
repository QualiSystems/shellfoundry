from setuptools import find_packages, setup


def get_file_content(file_name):
    with open(file_name) as f:
        return f.read()


readme = get_file_content("README.rst")
history = get_file_content("HISTORY.rst")
version = get_file_content("version.txt").strip()


setup(
    name="shellfoundry",
    version=version,
    description="shellfoundry - Quali tool for creating, "
    "building and installing CloudShell shells",
    long_description=f"{readme}\n\n{history}",
    long_description_content_type="text/markdown",
    author="Quali",
    author_email="info@quali.com",
    url="https://github.com/QualiSystems/shellfoundry",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={"shellfoundry": ["data/*.yml", "data/*.json"]},
    entry_points={"console_scripts": ["shellfoundry = shellfoundry.bootstrap:cli"]},
    include_package_data=True,
    install_requires=get_file_content("requirements.txt"),
    tests_require=get_file_content("test_requirements.txt"),
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords="shellfoundry sandbox cloud virtualization "
    "vcenter cmp cloudshell quali command-line cli",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: Apache Software License",
    ],
    python_requires=">=3.9, <3.14",
    test_suite="tests",
)
