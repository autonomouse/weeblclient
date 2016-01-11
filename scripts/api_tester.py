#! /usr/bin/env python2
from weeblclient.weebl_python2.weebl import Weebl
from pprint import pprint

username = '' # Enter your username here (e.g. CanonicalOilCiBot)
apikey = ''  # Enter api_key (e.g. 8aa0ca63966d78b3099b2759289f239ffdc9d7b6)
             # (Please note: That isn't the real api_key for oil-ci-bot!)

weebl_url = "http://10.245.0.14"
jenkins_host = "http://oil-jenkins.canonical.com"

# Production:
# environment_name = "production"
# environment_uuid = "124591ef-361d-4a33-a756-fa79b3b7a1f8"

# Staging:
# environment_name = "prod_staging"
# environment_uuid = "76fbbe93-192a-4a96-b1e2-dbada08fa5db"

# Integration:
environment_name = "integration"
environment_uuid = "7c82e43a-f5d6-47fb-ad9c-7d45c7ff48a7"

weebl = Weebl(environment_uuid,
              environment_name,
              username=username,
              apikey=apikey,
              weebl_url=weebl_url)
weebl.weeblify_environment(jenkins_host)

pprint(weebl.get_instances('environment'))
