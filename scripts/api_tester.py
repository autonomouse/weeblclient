#! /usr/bin/env python2
from weeblclient.weebl_python2.weebl import Weebl
from pprint import pprint

username = 'oil-ci-bot'
apikey = '8aa0ca63966d78b3099b2759289f239ffdc9d7b6'

weebl_url = "http://localhost:8000"
# weebl_url = "http://10.245.0.14"
jenkins_host = "http://oil-jenkins.canonical.com"

# Production:
# environment_name = "production"
# environment_uuid = "124591ef-361d-4a33-a756-fa79b3b7a1f8"

# Integration:
environment_name = "integration"
environment_uuid = "7c82e43a-f5d6-47fb-ad9c-7d45c7ff48a7"

weebl = Weebl(environment_uuid, environment_name, username, apikey,
              weebl_url=weebl_url)
weebl.weeblify_environment(jenkins_host)

pprint(weebl.get_instances('environment'))
