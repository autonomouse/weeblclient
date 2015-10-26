#! /usr/bin/env python2
from weeblclient.weebl_python2.weebl import Weebl


# Placeholder values, edit accordingly:
jenkins_host = "http://oil-jenkins.canonical.com"
mockDB = "/usr/share/doberman/samples/mock_database.yml"
environment_name = "production"
environment_uuid = "124591ef-361d-4a33-a756-fa79b3b7a1f8"
weebl_url = "http://10.245.0.14"

weebl = Weebl(environment_uuid, environment_name, weebl_url=weebl_url)
weebl.weeblify_environment(jenkins_host)
weebl.upload_bugs_from_yaml(mockDB)
