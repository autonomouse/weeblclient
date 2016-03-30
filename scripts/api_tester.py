#! /usr/bin/env python2
from weeblclient.weebl_python2.weebl import Weebl
from pprint import pprint

environment = 'local'
username = '' # Enter your username here (e.g. CanonicalOilCiBot)
apikey = ''  # Enter api_key (e.g. 8aa0ca63966d78b3099b2759289f239ffdc9d7b6)
             # (Please note: That isn't the real api_key for oil-ci-bot!)

environment_settings = {
    'production': {
        'weebl_url': "http://10.245.0.14",
        'jenkins_host': "http://oil-jenkins.canonical.com",
        'environment_name': "production",
        'environment_uuid': "124591ef-361d-4a33-a756-fa79b3b7a1f8",
    },
    'staging': {
        'weebl_url': "http://10.245.0.14",
        'jenkins_host': "http://oil-jenkins.staging.canonical.com/",
        'environment_name': "prod_staging",
        'environment_uuid': "76fbbe93-192a-4a96-b1e2-dbada08fa5db",
    },
    'integration': {
        'weebl_url': "http://10.245.162.53",
        'jenkins_host': "http://10.245.162.43:8080",
        'environment_name': "integration",
        'environment_uuid': "7c82e43a-f5d6-47fb-ad9c-7d45c7ff48a7",
    },
    'local': {
        'weebl_url': "http://localhost:8000",
        'jenkins_host': "http://oil-jenkins.canonical.com",
        'environment_name': "Sample Environment 2",
        'environment_uuid': "97cd0ea8-e0cc-43a7-8e93-af4797e1adf1",
    },
}
# Please note: the environment_uuid is liable to change with each fake_data cmd

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
