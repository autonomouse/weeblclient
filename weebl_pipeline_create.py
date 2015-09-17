#!/usr/bin/python

from weeblclient.weebl_python2.weebl import Weebl
from doberman.analysis.crude_jenkins import Jenkins
from doberman.common.CLI import CLI
from oil_ci.common.utils import get_config

from ConfigParser import ConfigParser
from os import environ
from string import lstrip
from sys import exit, argv


# new section added to /etc/oil-ci/oil-ci.conf:
#[weebl]
#uuid = 124591ef-361d-4a33-a756-fa79b3b7a1f8
#weebl_url = http://10.0.3.23:8000

class PipelineParametersFileWrapper(object):
    """ File wrapper to deal with non-yaml compliant parameters file.
    Expected format for each line is: "export NAME=value"
    Addresses these 2 issues:
    - missing section header: inject "[DEFAULT]" section
    - "export" keywords: remove them from every line
    """
    def __init__(self, fp):
        self.fp = fp
        self.section_header = '[DEFAULT]\n'

    def readline(self):
        if self.section_header:
            try: 
                return self.section_header
            finally: 
                self.section_header = None
        else: 
            return lstrip(self.fp.readline(), 'export ')


def read_pipeline_parameters(pipeline_params_file):
    params = ConfigParser()
    params.readfp(PipelineParametersFileWrapper(open(pipeline_params_file)))
    return params


def main(argv):
    if len(argv) != 2:
        print "Syntax: pipeline_weebl.py <pipeline_params_file>"
        exit(1)

    pipeline_params = read_pipeline_parameters(argv[1])
    pipeline_id = pipeline_params.get('DEFAULT', 'pipeline_id')

    oil_config = get_config()
    jenkins_url = oil_config.get('jenkins', 'url')
    environment = oil_config.get('jenkins', 'environment')
    weebl_uuid = oil_config.get('weebl', 'uuid')
    weebl_url = oil_config.get('weebl', 'weebl_url')
    build_executor_name = environ['NODE_NAME']

    cli = CLI().populate_cli()
    jenkins = Jenkins(cli)
    weebl = Weebl(weebl_uuid, environment, weebl_url=weebl_url)
    weebl.weeblify_environment(jenkins_url, jenkins)
    weebl.create_pipeline(pipeline_id, build_executor_name)


if __name__ == "__main__":
    exit(main(argv))
