#! /usr/bin/env python2
import argparse
import yaml
from weeblclient.weebl_python2.weebl import Weebl
from weeblclient.weebl_python2.weebl import utils


username = '' # Enter your username here (e.g. CanonicalOilCiBot)
apikey = ''  # Enter api_key (e.g. 8aa0ca63966d78b3099b2759289f239ffdc9d7b6)
             # (Please note: That isn't the real api_key for oil-ci-bot!)

default_jenkins_host = "http://10.245.162.43:8080/"
default_mockDB = "/home/darren/Repositories/Canonical/doberman/trunk/samples/mock_database.yml"
default_environment_name = "integration"
default_environment_uuid = "7c82e43a-f5d6-47fb-ad9c-7d45c7ff48a7"
default_weebl_url = "http://10.245.162.53/"

def parse():
    parser = argparse.ArgumentParser(description='Upload bugs to Weebl.')
    parser.add_argument('-d', '--dryrun', default=False, action='store_true',
                        help='Does not make any changes to the database.')
    parser.add_argument('-j', '--jenkins', default=default_jenkins_host,
                        help='URL of the jenkins instance for environment.')
    parser.add_argument('-f', '--file', default=default_mockDB,
                        help='YAML file containing bugs to be uploaded.')
    parser.add_argument('-n', '--name', default=default_environment_name,
                        help='Environment name (e.g. "production").')
    parser.add_argument('-u', '--uuid', default=default_environment_uuid,
                        help='Environment UUID.')
    parser.add_argument('-w', '--weebl', default=default_weebl_url,
                        help='URL of Weebl.')
    return parser.parse_args()

def find_new_or_alterated_bugs(local_db, remote_db):
    altered_bugs = {'bugs': {}}
    altered_bug_nums = []
    variable = [u'category', u'affects', u'description']
    for remote_bugno, remote_data in remote_db['bugs'].items():
        if str(remote_bugno) in local_db['bugs']:
            # Find out which bugs have changed so we only upload those:
            local_data = local_db['bugs'][str(remote_bugno)]
            jobs = [key for key in remote_data.keys() if key not in variable]
            different = False
            for job in jobs:
                if different == True:
                    continue
                if job in local_data and local_data[job] != remote_data[job]:
                    for item in local_data[job]:
                        if different == True:
                            break
                        for target_file_glob, value in item.items():
                            for regex in value['regexp']:
                                if [thing for thing in remote_data[job] if regex not in thing[target_file_glob]['regexp']] != []:
                                    different = True
            if different:
                altered_bug_nums.append(remote_bugno)

    # Find any bugs that are in local_db that aren't in remote_db:
    new_bugs = [local_bugno for local_bugno, jnk in local_db['bugs'].items() if
                local_bugno != 'GenericBug_Ignore' and int(local_bugno) not in
                remote_db['bugs']]
    altered_bug_nums.extend(new_bugs)
    for alt_bug in altered_bug_nums:
        altered_bugs['bugs'][alt_bug] = local_db['bugs'][str(alt_bug)]
    return altered_bugs

def main():
    args = parse()
    weebl = Weebl(args.uuid,
                  args.name,
                  username=username,
                  apikey=apikey,
                  weebl_url=default_weebl_url)
    weebl.weeblify_environment(args.jenkins)
    with open(args.file, 'r') as f:
        db = yaml.load(f.read())
    existing_bugs = weebl.get_bug_info()
    print("Uploading bugs from {}".format(args.file))
    bugs = find_new_or_alterated_bugs(db, existing_bugs)
    if args.dryrun:
        include_generics = False
        entry_list = utils.generate_bug_entries(bugs, include_generics)
        print
        if len(entry_list) == 0:
            print("No new bugs to upload.")
        for entry in entry_list:
            print('Bug #{0}. Regex: "{3}" (in {1} file: {2})'.format(*entry))
            print
    else:
        weebl.upload_bugs_from_bugs_dictionary(bugs)

if __name__ == '__main__':
    main()
