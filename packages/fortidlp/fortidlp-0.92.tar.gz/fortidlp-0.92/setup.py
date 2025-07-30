import os
from setuptools import find_packages, setup
from setuptools.command.install import install
cur_dir = os.path.dirname(__file__)

with open(f"{cur_dir}/requirements.txt") as f:
    required_packages = f.read().splitlines()

setup(
    name="fortidlp",
    version="0.92",
    description="This FortiDLP module is an open-source Python library that simplifies interaction with the FortiDLP Cloud API.",
    author="Rafael Foster",
    author_email="rafaelgfoster@gmail.com",
    project_urls={
        "GitHub": "https://github.com/rafaelfoster/fortidlp",
    },
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=required_packages,
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
    ]
)