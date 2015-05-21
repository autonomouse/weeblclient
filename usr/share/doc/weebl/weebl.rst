Preamble
========

- This section document the Weebl project. 
- To build html version, run:
    | pandoc usr/share/doc/weebl/weebl.rst -o usr/share/doc/weebl/weebl.html
- Then this doc can be viewed as a webpage:
    | firefox usr/share/doc/weebl/weebl.html

Requirements
============

- Ubuntu 15.04 (Vivid Vervet)
- Python 3
- Django 1.7
- PostgreSQL 9.4

Initial set up
==============

Development Notes
~~~~~~~~~~~~~~~~~

- During this development phase, please note the following.
    - The installation instructions below are for the development branch only. Once the deployment and packaging branches are merged in, and vivid is released, the following will not be necessary.
    - A prepopulated testing database will be added, and also a makefile to automatically set up a database deploy will be added, removing the need to do any of this manually.


Installation of Django 1.7 on pre-vivid releases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- To avoid using pip and instead use vivid repositories on earlier releases (such as utopic), do the following: 
    - sudo vi /etc/apt/preferences.d/vivid-manual-only 
        | Package: * 
        | Pin: release n=vivid 
        | Pin-Priority: 99  
        
    - grep '\sutopic\s' /etc/apt/sources.list | sudo tee /etc/apt/sources.list.d/vivid.list
    - sudo sed 's/utopic/vivid/g' -i /etc/apt/sources.list.d/vivid.list 
    - sudo apt-get update 
    - apt-cache policy python3-django 
    - sudo apt-get install python-django-common/vivid 
    - sudo apt-get install python3-sqlparse/vivid 
    - sudo apt-get install python3-django/vivid 
    - source: http://askubuntu.com/questions/569339/install-vagrant-version-1-5-or-greater-on-14-10

Dependencies
~~~~~~~~~~~~

- These modules will eventually be automatically installed as part of the packaging branch (This information will then be found in debian/control). At which time, these instructions will be updated. During development, however, the following will need to be installed:
    - python3 (>= 3.4.0) 
    - python3-django (>= 1.7.0) 
    - postgresql-9.4
    - python3-django-tastypie
    - python3-yaml
    - python3-mimeparse
    - python3-dateutil
    - python3-requests
    - python3-psycopg2
    - apache2
    - python (>= 2.7)
    - python-selenium 
    - build-essential

Postgres Installation
~~~~~~~~~~~~~~~~~~~~~

- The tests will not work until you have set up a database on your machine for it to connect to
- Install Postgres
    - sudo apt-get install postgresql
    - sudo apt-get install python3-psycopg2
- sudo su - postgres
    | createdb bugs_database
    | createuser user -P
    | psql
    | GRANT ALL PRIVILEGES ON DATABASE bugs_database TO "user";
    | ALTER USER "user" CREATEDB;
    | createdb bugs_database
    | exit (Cntl-D) and exit
- then
    | weebl/manage.py syncdb

Running tests
~~~~~~~~~~~~~
 
- Run unit tests using:
| ./run_tests.sh unit
- Run linter using:
| ./run_tests.sh lint

- When Selenium2 for Python3 is supported in the vivid repositories, you will be able to run functional (webdriver) tests using:
| ./run_tests.sh func


Deployment
~~~~~~~~~~

- Weebl is not yet production ready (these instrutions will be updated with Apache hosting instructions as Weebl is developed), and so it is currently deployed using django's built-in server:
    | sudo ./weebl/manage.py runserver 0.0.0.0:8000


Making Changes and Packaging Weebl
==================================

- http://www.laurentluce.com/posts/hello-world/
- Update changelog 
- Create a duplicate of changelog called changelog.Debian
    | cp changelog changelog.Debian
- Copy these files over to usr/share/doc/weebl/ and compress them:
    | cp changelog usr/share/doc/weebl/
    | mv changelog.Debian usr/share/doc/weebl/
    | gzip -f --best usr/share/doc/weebl/changelog
    | gzip -f --best usr/share/doc/weebl/changelog.Debian    
- Fix permissions of package files:
    | find . -type d | xargs chmod 0755
- Create the package (this assumes the weebl directory is called trunk and the version number is 0.0.1-0ubuntu1):
    | cd ..
    | fakeroot dpkg-deb --build trunk
    | mv trunk.deb weebl_0.0.1-0ubuntu1.deb
- Check package for errors:
    | lintian weebl_0.0.1-0ubuntu1.deb


