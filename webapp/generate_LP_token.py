#! /usr/bin/env python2

import os
from launchpadlib.launchpad import Launchpad
from launchpadlib.credentials import Credentials
from CredentialStore import CredentialStore


consumer_key = "webapp_generator"
output_dir = "~/.config/lpltk/"


output_loc = os.path.expanduser(os.path.join(output_dir, 
                                             "credentials-production"))
credentials = Credentials(consumer_key)
cred_store = CredentialStore()
url = credentials.get_request_token(web_root="production")
print
print("Go to {} to authorise '{}'.".format(url, consumer_key))
print
jnk = raw_input("Once authorised, press any key to continue.")
print
try:
    credentials.exchange_request_token_for_access_token(web_root="production")
    
    # Extract token details:
    token = []
    token.append("[1]")
    token.append("consumer_key = {}".format(credentials.consumer.key))
    token.append("consumer_secret = {}".format(credentials.consumer.secret))
    token.append("access_token = {}".format(credentials.access_token.key))
    token.append("access_secret = {}".format(credentials.access_token.secret))
    
    # Write to file:
    with open(output_loc, 'w') as config:
        config.write("\n".join(token))
    
except Exception, e:
    print
    print("Uh-oh, something went horribly wrong:\n{}".format(e))
