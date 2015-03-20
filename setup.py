#!/usr/bin/env python3
from setuptools import setup, find_packages

import weebl

setup(
    name="weebl",
    version=weebl.__version__,
    description="Web App for OIL",
    author="Darren Hoyland",
    author_email="<darren.hoyland@canonical.com>",
    url="http://launchpad.net/weebl",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers"],
    entry_points={
        "console_scripts": [
            'weebl = weebl.scripts.weebl:main',
        ]
        },
    )
