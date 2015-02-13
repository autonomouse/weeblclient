#!/usr/bin/python

from distutils.core import setup
from arsenal import info
import glob, os, re

# look/set what version we have
changelog = "debian/changelog"
if os.path.exists(changelog):
    head=open(changelog).readline()
    match = re.compile(".*\((.*)\).*").match(head)
    if match:
        version = match.group(1)

setup(
    name             = info.PROGNAME,
    version          = version,
    url              = info.URL,
    author           = info.LEAD_DEVELOPER.name,
    author_email     = info.LEAD_DEVELOPER.email,
    description      = info.SHORT_DESCRIPTION,
    long_description = info.DESCRIPTION,
    license          = info.LICENSE_URL,
    platforms        = ['any'],
    requires = ['pydoctor', 'pep8',
                'json',
                'launchpadlib', 'lpltk',
                'cgitb', 'pycurl', 'bzutils',
                'mako', 'ipdb'],
    packages=[
        'arsenal',
        'arsenal.filters',
        'arsenal.utils'],
    package_data = {
        },
    data_files = [
        ('share/templates',                  glob.glob('data/templates/*.*')),
        ('share/css',                        glob.glob('data/css/*.*')),
        ('share/js',                         glob.glob('data/js/*.*')),
        ('share/img',                        glob.glob('data/img/*.*')),
        ],
    scripts=glob.glob('scripts/*'),
    )

# Uninstallation:
#
# rm -rf /var/lib/arsenal
# rm -rf /var/www/+icing
# rm /usr/local/lib/python2.6/dist-packages/arsenal-0.0.egg-info
# rm /usr/lib/cgi-bin/upstreamer.cgi
# rm /var/www/js/sorttable.js /var/www/js/sortable.js /var/www/js/filtertable.js
# rm /usr/local/bin/<scripts> # see above
