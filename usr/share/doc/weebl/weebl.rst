Preamble
========

- This section document the Weebl project. 
- To build html version, run:
    | pandoc usr/share/doc/weebl/weebl.rst -o usr/share/doc/weebl/weebl.html
- Then this doc can be viewed as a webpage:
    | firefox usr/share/doc/weebl/weebl.html

Requirements
============

- Python 3
- Django 1.7
- PostgreSQL 9.4
- Selenium 2

Initial set up
==============

Installation of Django 1.7 on pre-vivid releases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- To avoid using pip, I did this: 
    - cat <<EOF | sudo tee /etc/apt/preferences.d/vivid-manual-only 
        | Package: * 
        | Pin: release n=vivid 
        | Pin-Priority: 99 
        | EOF - grep '\sutopic\s' /etc/apt/sources.list 
        | sudo tee /etc/apt/sources.list.d/vivid.list 
    - sudo sed 's/utopic/vivid/g' -i /etc/apt/sources.list.d/vivid.list 
    - sudo apt-get update 
    - apt-cache policy python3-django 
    - sudo apt-get install python-django-common/vivid 
    - sudo apt-get install python3-sqlparse/vivid 
    - sudo apt-get install python3-django/vivid 
    - source: http://askubuntu.com/questions/569339/install-vagrant-version-1-5-or-greater-on-14-10

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

Selenium Installation
~~~~~~~~~~~~~~~~~~~~~

 - *This section needs updating to avoid the use of pip*
 - sudo pip3 install selenium 

Running tests
~~~~~~~~~~~~~
 
- Run functional (webdriver) tests using:
| ./run_tests.sh func
- Run unit tests using:
| ./run_tests.sh unit
- Run linter using:
| ./run_tests.sh lint


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


