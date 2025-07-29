from setuptools import setup
from setuptools import find_namespace_packages
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), "r") as fd:
    long_description = fd.read()

setup(
    name='jfrog-downloader',
    version='1.0.3',
    description='Downloading Images from Jfrog',
    license="Apache License 2.0",
    author='abi-sheak',
    author_email='abisheakkumarasamy@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(),
    py_modules=['JFROGDownloader'],
    install_requires=["jfrgdownload", "abisheak"],
    python_requires='>=3.6',
)