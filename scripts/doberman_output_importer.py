#! /usr/bin/env python2
import os
import pytz
import parsedatetime as pdt
from weeblclient.weebl_python2.weebl import Weebl

data_dir = "/home/darren/triage/production_data/gen_oil_stats/builds"

weebl = Weebl("124591ef-361d-4a33-a756-fa79b3b7a1f8",
              "production",
              weebl_url="http://10.245.0.14")
              #weebl_url="http://localhost:8000")

for doberman_out_folder in os.listdir(data_dir):
    full_path = os.path.join(data_dir, doberman_out_folder)
    if 'archive' in os.listdir(full_path):
        output_dir = os.path.join(
            data_dir, doberman_out_folder, "archive/artifacts")
    else:
        output_dir = full_path

    timestamp = None
    try:
        val = pdt.Calendar(pdt.Constants(usePyICU=False)).parse(
            doberman_out_folder)
        timestamp = pytz.utc.localize(datetime(*val[0][:6]))
    except:
        pass
    weebl.import_data_from_doberman_output_folder(output_dir, timestamp)
