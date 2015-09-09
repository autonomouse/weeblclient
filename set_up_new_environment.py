#!/usr/bin/python
import sys
from client.weebl_python2.weebl import Weebl
from client.weebl_python2.weebl import Weebl
from doberman.analysis.crude_jenkins import Jenkins


class SetUpNewEnvironment(object):

    def __init__(self, weebl_ip, weebl_api_ver, weebl_auth):
        self.message = 1  # A non-zero exit status is regarded as a failure.
        self.weebl = Weebl(self.cli)
        self.jenkins = Jenkins(self.cli)
        self.weebl.weeblify_environment(self.jenkins.jenkins_api, report=True)
        self.message = 0  # A zero exit status is regarded as a pass.

def main():
    weebl_ip = "http://10.245.0.14"
    weebl_api_ver = "v1"
    weebl_auth = ('weebl', 'passweebl')
    setup = SetUpNewEnvironment(weebl_ip, weebl_api_ver, weebl_auth)
    return setup.message


if __name__ == "__main__":
    sys.exit(main())
