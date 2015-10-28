#! /usr/bin/env python2
import yaml
from weeblclient.weebl_python2.weebl import Weebl


# Placeholder values, edit accordingly:
jenkins_host = "http://oil-jenkins.canonical.com"
mockDB = "/usr/share/doberman/samples/mock_database.yml"
environment_name = "production"
environment_uuid = "124591ef-361d-4a33-a756-fa79b3b7a1f8"
weebl_url = "http://10.245.0.14"
force_refresh = False

weebl = Weebl(environment_uuid, environment_name, weebl_url=weebl_url)
weebl.weeblify_environment(jenkins_host)

if force_refresh is True:
    print("Dissociating all regexes from existing target files and jobs.")
    weebl.clear_target_files_and_jobs_from_known_bug_regexes()
    print("Complete. Now reassociating with bug regexes from yaml file.")

print("Uploading bugs from {}".format(mockDB))
with open(mockDB, 'r') as f:
    db = yaml.load(f.read())
weebl.upload_bugs_from_bugs_dictionary(db)
