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


API Specification
=================

Authentication
--------------

- There is currently no authentication on the API.

Quick Start
-----------

- For now to upload data (report_status data in this case) do the following:
    | curl --dump-header - -H "Content-Type: application/json" -X PUT --data '{}' http://localhost/api/<v>/jenkins/<UUID>/

- or if using python requests:
    | url = 'http://localhost/api/<v>/jenkins/<UUID>/'
    | headers = {"content-type":"application/json"}
    | data = {}
    | requests.post(url, headers=headers, data=json.dumps(data)).text

- This can then be seen by:
    | curl --dump-header - -H "Content-Type: application/json" -X GET http://localhost/api/<v>/jenkins/<UUID>/

- or by going to:
    | http://localhost/api/<v>/jenkins/<UUID>/

Response Codes
--------------

Weebl utilises Tasypie's response codes, which should be the `standard html response codes`_.

.. _standard html response codes: http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html

Error Codes
-----------

In addition to the response codes, Weebl will also implement `Twitter-style error codes`, although these are yet to be implemented.

.. _Twitter-style error codes: https://dev.twitter.com/overview/api/response-codes

They will eventually be listed here:

====   =============================    ==============================================================================
Code   Text                             Description
====   =============================    ==============================================================================
0      Authentication problem           Could not authenticate the credentials provided
100    WeeblSetting does not exist      The instance of WeeblSetting does not exist
101    Environment does not exist       The instance of Environment does not exist
102    ServiceStatus does not exist     The instance of ServiceStatus does not exist
103    Jenkins does not exist           The instance of Jenkins does not exist
====   =============================    ==============================================================================





Headers
-------

{"content-type":"application/json"}

General Response Info
---------------------

- Tastypie has some useful built-in responses for collection URIs (e.g. a GET on /api/<v>/environment/):
    - "meta":
        - a dictionary of helpful summary information
        - e.g. {"limit": 20, "next": null, "offset": 0, "previous": null, "total_count": 2}
    - "objects":
        - a list of dictionaries containing the requested info

Resource Specification
----------------------

- Below are tables for each end-point, where <v> represents the api version number (for example "v1"), <UUID> represents the uuid of the environment instance and <uuid> represents a uuid for the given model:

================================    =========================================   =============   ========================================    =============================================================================
Purpose                             End-point                                   HTTP Method     Data                                        Notes
================================    =========================================   =============   ========================================    =============================================================================
Create environment                  /api/<v>/environment/                       POST            {'name': 'production'} or {}                If 'name' not supplied, will use UUID as name.
List all environments               /api/<v>/environment/                       GET
Show environment with this name     /api/<v>/environment/by_name/production/    GET
Show environment with this UUID     /api/<v>/environment/<UUID>/                GET
Update enviornment                  /api/<v>/environment/<UUID>/                PUT             {'name': 'production'}                      Changing the UUID by this method is not allowed
Delete the environment with UUID    /api/<v>/environment/<UUID>/                DELETE

Create jenkins                      /api/<v>/jenkins/                           POST            {'environment': <UUID>,                     Required: 'environment', 'external_access_url'
                                                                                                 'external_access_url': <jenkins_url>}      Optional: 'internal_access_url' (defaults to 'external_access_url')
                                                                                                or
                                                                                                {'environment': <UUID>,
                                                                                                 'external_access_url': <jenkins_url>,
                                                                                                 'internal_access_url': <url>}
List all jenkins                    /api/<v>/jenkins/                           GET
Show jenkins with this env UUID     /api/<v>/jenkins/<UUID>/                    GET
Update jenkins                      /api/<v>/jenkins/<UUID>/                    PUT             {'external_access_url': <jenkins_url>,      Can supply 'external_access_url', 'internal_access_url', both or none ({}).
                                                                                                 'internal_access_url': <url>}              'service_status_updated_at' will update automatically
                                                                                                                                            Changing the environment UUID or 'service_status_updated_at' is not allowed.
Delete the jenkins                  /api/<v>/jenkins/<UUID>/                    DELETE

List service_status                 /api/<v>/service_status/                    GET
Show individual service_status      /api/<v>/service_status/<integer>/          GET

Create build_executor               /api/<v>/build_executor/                    POST            {'jenkins': <UUID>}                         If 'name' not supplied, will use its uuid as name.
                                                                                                or
                                                                                                {'name': '<ci-oil-master/slaveXX-X>',
                                                                                                 'jenkins': <UUID>}
List all build_executors            /api/<v>/build_executor/                    GET
Show environment with this uuid     /api/<v>/build_executor/<uuid>/             GET
Update build_executor               /api/<v>/build_executor/<uuid>/             PUT             {'jenkins': <UUID>}                         Changing the UUID by this method is not allowed
                                                                                                or
                                                                                                {'name': '<ci-oil-master/slaveXX-X>',
                                                                                                 'jenkins': <UUID>}                     
Delete the build_executor           /api/<v>/build_executor/<uuid>/             DELETE
================================    =========================================   =============   ========================================    =============================================================================





Other things to consider (remove this section when done)
--------------------------------------------------------
- parameters resources
- response format
- plural versus singular (act on lists or one at a time)
- consistency
