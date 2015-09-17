#!/usr/bin/python
from setuptools import setup, find_packages
import six


if six.PY3:
    import weebl
    import tasks
    setup(
        name="weebl",
        version=weebl.__version__,
        description="Web App for OIL",
        author="Darren Hoyland",
        author_email="<darren.hoyland@canonical.com>",
        url="http://launchpad.net/weebl",
        packages=find_packages(exclude=['weeblclient*']),
        include_package_data=True,
        classifiers=[
            "Development Status :: 2 - Pre-Alpha",
            "Programming Language :: Python3",
            "Topic :: Internet",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Intended Audience :: Developers"],
        entry_points={
            "console_scripts": [
                'weebl_setup = set_up_new_environment:main',
            ]
        },
    )
else:
    # should really check six.PY2 and raise exception if not -- but version
    # in precise non-updates is ancient and does not have that attribute
    import weeblclient
    from weeblclient import weebl_python2
    setup(
        name="weeblclient",
        version=weebl_python2.__version__,
        description="Web App for OIL client",
        author="Darren Hoyland",
        author_email="<darren.hoyland@canonical.com>",
        url="http://launchpad.net/weebl",
        packages=find_packages(exclude=['weebl', 'weebl.*']),
        include_package_data=True,
        classifiers=[
            "Development Status :: 2 - Pre-Alpha",
            "Programming Language :: Python",
            "Topic :: Internet",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Intended Audience :: Developers"
        ],
    )
