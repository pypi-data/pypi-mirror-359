# -*- coding:utf-8 -*-
import os
from setuptools import find_packages
from setuptools import setup

install_requires = ["pytest", "mnemonic", "web3", "bip44"]

version = {}
with open(os.path.join("yeying/version.py")) as fp:
    exec(fp.read(), version)

setup(
    name="yeying_client",
    version=version["__version__"],
    description="yeying python sdk",
    url="https://github.com/yeying-community/yeying-client-python",
    author="yeying-community",
    author_email="yeying.community@gmail.com",
    install_requires=install_requires,
    packages=find_packages(),
    entry_points={"console_scripts": [
        "yeying_cmd=yeying.client.tool.cmd.__main__:main",  # noqa
    ]},
)
