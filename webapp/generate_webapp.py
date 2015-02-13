#! /usr/bin/env python2

import sys
import os
import glob
import subprocess
import multiprocessing as mp
import re
import time
import shutil
import json
from webapp_builder import WebAppBuilder
from pprint import pprint


def main():

    ### TO BE MOVED TO A CONF FILE:
    # Options:
    projects = ['OIL', 'MAAS']
    make_webapp = ['OIL']
    collect_data = True
    reload_bugs = True
    dbglvl = 'info'

    # Arsenal:
    file_path = os.path.abspath(os.path.dirname(__file__))
    arsenal_directory = os.path.abspath(os.path.join(file_path, 
                                        "../arsenal-devel/"))
    arsenal_scripts = os.path.join(arsenal_directory, "scripts")
    arsenal_templates = os.path.join(arsenal_directory, "web/templates")
    arsenal_reports = os.path.join(arsenal_directory, "reports")

    # Doberman:
    doberman_directory = '.'
    reformer_command = ["DOBERMAN_ROOT=`pwd`", 
                        "PYTHONPATH=$PYTHONPATH:`pwd`", 
                        "python", 
                        "doberman/scripts/reformer"]
     
    ### END OF CONF FILE STUFF    
    
    
    # Define an output queue
    output = mp.Queue()
    
    processes = []
    
    for project in projects:
        path = os.path.abspath(os.path.join(arsenal_reports, project))
        for file_location in glob.glob(os.path.join(path, '*.json')):
            title = file_location.split('/')[-1].strip('.json')
            processes.append(mp.Process(target=run_arsenal, args=(output, 
                             project, title, file_location, arsenal_scripts, 
                             arsenal_templates, collect_data, reload_bugs, 
                             dbglvl)))

    
    # Run processes
    [proc.start() for proc in processes]
    
    # Exit the completed processes
    [proc.join() for proc in processes]

    # Get process results from the output queue
    results = [output.get() for proc in processes]
    pprint(results)
    
    return -1 if -1 in [res[0] for res in results] else 0
    
def run_arsenal(output, project, title, json_loc, arsenal_scripts,
                arsenal_templates, collect_data, reload_bugs, dbglvl):
    try:
        # Collect bug data:
        if collect_data:
            collect_bug_data = [os.path.abspath(os.path.join(arsenal_scripts, 
                                "collect-bug-data"))]
            cbd_args = ['--privates', '--reload-bugs', 
                        '--debug={}'.format(dbglvl), json_loc]
                        
            collect_bug_data.extend(cbd_args)
            subprocess.call(collect_bug_data)
        
        # Generate web-page:
        reporter = [os.path.abspath(os.path.join(arsenal_scripts, 
                                                 "reporter"))]
        r_args = ['--title={}'.format(title), 
                  '--template={}/bugs-by-tag.mako'.format(arsenal_templates), 
                  json_loc]
        reporter.extend(r_args)
        html_output = subprocess.check_output(reporter)
        html_loc = re.sub('json$', 'html', json_loc)
        with open(html_loc, 'w') as html:
            html.write(html_output)
        
        # Generate companion webapp (only really for OIL at the moment):
        if title in make_webapp:
            build_webapp = WebAppBuilder(project, title, json_loc, 
                                         arsenal_scripts, arsenal_templates)            

        # report back to user:
        mission_accomplished = 1
        message = "{} generated.".format(html_loc)
    except Exception:
        mission_accomplished = -1
        message = "No data"
    finally:
        output.put((mission_accomplished, message))

def mkdir(directory):
    """ Make a directory, check and throw an error if failed. """
    if not os.path.isdir(directory):
        try:
            os.makedirs(directory)
        except OSError:
            if not os.path.isdir(directory):
                raise
                
if __name__ == "__main__":
    sys.exit(main())    
    
