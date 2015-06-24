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

- Run ./install_deps before attempting to use invoke (see 'Deployment')

Deployment
~~~~~~~~~~

- To deploy on a django's built in test server:
    | sudo invoke go production -s run_server
    
- To deploy on Apache:
    | sudo invoke go production
    
- In case of catestrophic failure, you can dump the production database by doing the following (please note that there is no data backup facility yet, so not recommended *at all* once we start populating the database with actual data):
    | sudo invoke destroy production



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
