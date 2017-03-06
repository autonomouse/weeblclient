from setuptools import setup, find_packages
import weeblclient

setup(
    name="weeblclient",
    version=weeblclient.__version__,
    description="Web App for OIL client",
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
        "Intended Audience :: Developers"
    ],
)
