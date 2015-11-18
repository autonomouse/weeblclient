#! /usr/bin/env python2
import os
import pytz
import parsedatetime as pdt
from weeblclient.weebl_python2.weebl import Weebl


username = '' # Enter your username here (e.g. CanonicalOilCiBot)
apikey = ''  # Enter api_key (e.g. 8aa0ca63966d78b3099b2759289f239ffdc9d7b6)
             # (Please note: That isn't the real api_key for oil-ci-bot!)
environment_name = "production"
environment_uuid = "124591ef-361d-4a33-a756-fa79b3b7a1f8"
weebl_url = "http://10.245.0.14"

# Alter data_dir as appropriate:
data_dir = "/home/ubuntu/production_data/gen_oil_stats/builds"

weebl = Weebl(environment_uuid,
              environment_name,
              username=username,
              apikey=apikey,
              weebl_url=weebl_url)

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
