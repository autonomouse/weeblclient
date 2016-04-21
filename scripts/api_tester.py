#! /usr/bin/env python2
from weeblclient.weebl_python2.weebl import Weebl
from pprint import pprint
from env_selector import environment_settings
# create an env_selector.py file in this directory with an environment_settings
# directory containing the details of each env, similar to the following:
#environment_settings = {
#    'local': {
#        'weebl_url': "http://localhost:8000",
#        'jenkins_host': "http://jenkins.url",
#        'environment_name': "Local Environment",
#        'environment_uuid': "00aa0aa0-a0aa-00a0-0a00-aa0000a0aaa0",
#    },
#}
# This env_selector.py file will be ignored by git
from weebl_secrets import username, apikey
# create a weebl_secrets.py file in this directory with two lines in it:
# username = 'xxx'
# apikey = 'xxxxxxxxxxxx'
# This weebl_secrets.py file will be ignored by git

environment = 'local'

weebl = Weebl(environment_settings[environment]['environment_uuid'],
              environment_settings[environment]['environment_name'],
              username=username,
              apikey=apikey,
              weebl_url=environment_settings[environment]['weebl_url'])
weebl.weeblify_environment(environment_settings[environment]['jenkins_host'])

def display(model, keyname):
    obj = model.lower()
    print('')
    print(obj + "s:")
    print('')
    instance_keyname_set = {
        instance[keyname] for instance in weebl.get_instances(obj)['objects']}
    pprint(list(instance_keyname_set))
    print("-----------------------------------")
    print('')

display('environment', 'name')
display('buildexecutor', 'name')
