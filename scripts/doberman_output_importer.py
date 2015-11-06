#! /usr/bin/env python2
import os
from weeblclient.weebl_python2.weebl import Weebl
from doberman.analysis.crude_jenkins import Jenkins
from doberman.common.CLI import CLI
from doberman.common import utils

data_dir = "/home/darren/triage/production_data/gen_oil_stats/builds"

cli = CLI()
cli.netloc = "91.189.92.95"  # production
cli.offline_mode = True
cli.jenkins_host = "http://oil-jenkins.canonical.com"
cli.run_remote = False
cli.pysid = "dd8d6e5394898bb506b7b5291d0a57f6"
cli.LOG = utils.get_logger()
jenkins = Jenkins(cli)

jenkins_host = "http://oil-jenkins.canonical.com"

weebl = Weebl("124591ef-361d-4a33-a756-fa79b3b7a1f8",
              "production",
              #weebl_url="http://10.245.0.14")
              weebl_url="http://localhost:8000")
weebl.weeblify_environment(jenkins_host, jenkins)

for doberman_out_folder in os.listdir(data_dir):
    full_path = os.path.join(data_dir, doberman_out_folder)
    if 'archive' in os.listdir(full_path):
        output_dir = os.path.join(
            data_dir, doberman_out_folder, "archive/artifacts")
    else:
        output_dir = full_path

    weebl.import_data_from_doberman_output_folder(output_dir, doberman_out_folder)
