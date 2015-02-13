#!/usr/bin/python

import os
import simplejson as json
import sys

from datetime import datetime
from mako.template import Template

from arsenal.utils import date_to_string

def create_report(content, report_name):
    report = open(report_name, "w")
    report.write(content)
    report.close()


if __name__ == "__main__":
    json_file = sys.argv[1]
    with open(json_file, "r") as json_datafile:
        json_data = json_datafile.read()
        data = json.loads(json_data)
    template = Template(filename="%s/../web/templates/team-subbed-packages.mako" %
                        os.getcwd())
    content = template.render(report_title = "Team to Package Mapping",
        template_data = data,
        json_data_string = data,
        timestamp = date_to_string(datetime.utcnow()),
    )
    create_report(content, "m-r-package-team-mapping.html")
