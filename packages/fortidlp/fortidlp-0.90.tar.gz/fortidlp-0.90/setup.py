from setuptools import setup, find_packages

setup(
    name="fortidlp",
    version="0.90",
    author="Rafael Foster",
    author_email="rafaelgfoster@gmail.com",
    description="This FortiDLP module is an open-source Python library that simplifies interaction with the FortiDLP Cloud API.",
    packages=find_packages(),
    install_requires=["Requests==2.31.0"],
    license="MIT",
    license_files=("LICENSE"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
