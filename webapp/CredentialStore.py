#! /usr/bin/env python2

import pickle
from launchpadlib.credentials import Credentials, CredentialStore


class CredentialStore(CredentialStore):
    
    def do_save(self, credentials, unique_consumer_id):
        try:
            file_location = unique_consumer_id
            pickle.dump(credentials, open(file_location, "wb"))
            self.credential_save_failed = False
        except:
            self.credential_save_failed = True

    def do_load(self, unique_key):
        file_location = unique_key
        return pickle.load( open(file_location, "rb"))  
