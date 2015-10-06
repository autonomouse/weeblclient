#!/usr/bin/env python3
import os
import re
import sys
import psycopg2
import psutil
import shutil
from invoke import task, run
from datetime import datetime

application = 'weebl'
preamble = "WEEBL_ROOT=`pwd` PYTHONPATH=$PYTHONPATH:`pwd`"
apps = ['oilserver']
postgres_user = "postgres"
postgres_pwd = "passweebl"
test_user = "test_weebl"
prdctn_user = "weebl"
test_pwd = postgres_pwd
prdctn_pwd = postgres_pwd
test_db_name = "test_bugs_database"
prdctn_db_name = "bugs_database"
test_settings = "test_settings"
prdctn_settings = "settings"
sites_available_location = "/etc/apache2/sites-available/weebl.conf"
file_loc = os.path.dirname(os.path.abspath(__file__))
deploy_path = "{}/{}".format(file_loc, application)  # change
setup_file_loc = "setup.py"
jslibs_src_dir = "/usr/share/javascript/"
jslibs_dest_dir = os.path.join(file_loc, "weebl/oilserver/static/js/jslibs/")
jslibs_files = ['jquery/jquery.js',
                'angular.js/angular.js',
                'angular.js/angular-route.js',
                'angular.js/angular-cookies.js',
                'angular.js/angular-resource.js',
                'yui3/yui-base/yui-base-min.js',
                ]


''' REQUIRES install_deps to have been run first. '''

@task(default=True)
def list():
    """List all available tasks."""
    run("invoke --list")
    run('invoke --help')

@task(help={'database': "Type test or production",
            'server': "Defaults to Apache. Can alternatively user 'runserver'",
            'ip-addr': "IP to run server on. Defaults to 127.0.0.1.",
            'port': "Port to run server on. Defaults to 8000."})
def go(database, server="apache", ip_addr="127.0.0.1", port=8000):
    """Set up and run weebl using either a test or a production database."""
    copy_system_angularjs()
    initialise_database(database)
    deploy(ip_addr, port, server)

@task
def run_tests():
    """Run unit, functional, and lint tests for each app."""
    destroy_db(test_db_name, test_pwd, force=True, backup=False)
    copy_system_angularjs()
    initialise_database("test")
    load_fixtures()
    run_lint_tests()
    for app in apps:
        run_unit_tests(app)
    run_functional_tests()

@task(help={'database': "Type test or production"})
def createdb(database):
    """Set up and run weebl using either a test or a production database."""
    if database == "production":
        create_db_and_user(prdctn_db_name, prdctn_user, prdctn_pwd)
    elif database == "test":
        create_db_and_user(test_db_name, test_user, test_pwd)

@task
def syncdb():
    """Synchronise the django database."""
    migrate()

@task
def force_stop():
    """Kill all processes associated with the application."""
    for proc in psutil.process_iter():
        if application in repr(proc.cmdline()):
            file = proc.cmdline()[1] if len(proc.cmdline()) >= 2 else None
            msg = "Killing {} process id {}"
            if file:
                msg += ", run by {}"
            try:
                proc.kill()
                print(msg.format(proc.name(), proc.pid, file))
            except:
                print("Failed to kill {} process id {}."
                      .format(proc.name(), proc.pid))

@task(help={'database': "Type test or production",
            'force': "Destroy even if cannot back up data (not recommended!)"})
def destroy(database, force=False):
    """Destroy either the test or production database and user."""
    if database == "production":
        destroy_production_data(force)
    elif database == "test":
        destroy_test_data(force)

@task(help={'database': "Type test or production"})
def backup_database(database, force=False):
    """Backs up database to file."""
    timestamp = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
    backup_to = "Database_backup__{}__{}.json".format(database, timestamp)
    try:
        run("{}/manage.py dumpdata > {}".format(application, backup_to))
    except:
        msg = "Could not back up {0} database{1}."
        if force is True:
            print(msg.format(application, " - continuing anyway (force)"))
        else:
            print(msg.format(application, " - aborting"))
            return
    return backup_to

@task(help={'fixture': "Fixture to load into database"})
def load_fixtures(fixture="initial_settings.yaml"):
    print("Adding data from {} into database".format(fixture))
    run('{}/manage.py loaddata "{}"'.format(application, fixture))

def initialise_database(database):
    if database == "production":
        stngs = prdctn_settings
    elif database == "test":
        stngs = test_settings
    else:
        print("Please provide an option: either 'production' or 'test'")
        return
    set_postgres_password(postgres_pwd)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{0}.{1}"
                          .format(application, stngs))
    createdb(database)

@task()
def fake_data():
    initialise_database("production")
    print("Creating fake data...")
    run('{}/manage.py fake_data'.format(application))

@task(help={'filetype': "Format of output file (defaults to .png)"})
def schema(filetype="png"):
    run('{0}/manage.py graph_models -a > {0}.dot'.format(application))
    run('dot -T{1} {0}.dot -o {0}_schema.{1}'.format(application, filetype))
    run('rm {}.dot'.format(application))
    print("Schema generated at {0}_schema.{1}".format(application, filetype))

def migrate():
    """Make migrations and migrate."""
    run("{}/manage.py makemigrations".format(application), pty=True)
    run("{}/manage.py migrate".format(application), pty=True)

def create_production_db():
    create_db_and_user(prdctn_db_name, prdctn_user, prdctn_pwd)

def create_test_db():
    create_db_and_user(test_db_name, test_user, test_pwd)

def migrate_individual_app(application, app):
    run('{}/manage.py makemigrations {}'.format(application, app))
    run('{}/manage.py migrate {}'.format(application, app))

def destroy_test_data(force):
    rusure = "Are you sure you want to drop the test database and user?! (y/N)"
    if prompt(rusure, default='N', validate=yes_no):
        destroy_db(test_db_name, test_pwd, force=force)
        destroy_user(test_user, test_pwd)

def destroy_production_data(force):

    rusure1 = "You want to drop the PRODUCTION database (y/N)"
    rusure1 += " - are you absolutely sure about that?! (y/N)"
    rusure2 = "Really? I'll only ask one more time after this!!! (y/N)"
    rusure3 = "I don't believe you. Call me paranoid, but this is PRODUCTION "
    rusure3 += "data we're talking about! Type \"I am sure\" to proceed:\n>"
    rusure4 = "Are you sure you want to drop the user: {}?! (y/N)"

    if prompt(rusure1, default='N', validate=yes_no):
        if prompt(rusure2, default='N', validate=yes_no):
            if prompt(rusure3, default='N', validate=i_am_sure):
                destroy_db(prdctn_db_name, prdctn_pwd, force=force)
                user = prdctn_user
                if prompt(rusure4.format(user), default='N', validate=yes_no):
                    destroy_user(prdctn_user, prdctn_pwd)
                else:
                    print("User deletion aborted")
                return
    print("Phew - that was close...")

def create_db_and_user(db_name, user, pwd):
    create_user(user, pwd)
    create_database(db_name, user, pwd)

def db_cxn(sql, pwd, dbname='postgres', user='postgres', host='localhost',
           isolation_lvl=0):
    con = psycopg2.connect(dbname=dbname, user=user, host=host, password=pwd)
    con.set_isolation_level(isolation_lvl)
    cursor = con.cursor()
    try:
        cursor.execute(sql)
        response = cursor.fetchall()
    except psycopg2.ProgrammingError as e:
        response = e
    cursor.close()
    con.close()
    return response

def set_postgres_password(pwd):
    """Sets the superuser password - this is especially useful shortly after
    a new postgres installation as no default password is given and the user
    must first log in as root to change it. This should be run with 'sudo'.
    """
    sql = "alter user postgres with password '{}'".format(pwd)
    run('''sudo -u postgres psql -U postgres -d postgres -c "{}";'''
        .format(sql))

def check_if_user_exists(user, pwd):
    sql_check_user = "SELECT 1 FROM pg_roles WHERE rolname='{}'"
    sql = sql_check_user.format(user)
    try:
        return True if db_cxn(sql, pwd)[0][0] else False
    except:
        return False

def check_if_database_exists(database, pwd):
    sql = "SELECT * from pg_database where datname='{}'".format(database)
    out = db_cxn(sql, pwd)
    exists = False
    for element in out:
        if database in element:
            exists = True
    return exists

def destroy_db(database, pwd, force=False, backup=True):
    if backup:
        backup_to = backup_database(database, force)

    # Drop the database:
    sql = "DROP DATABASE IF EXISTS {}".format(database)
    db_cxn(sql, pwd)
    succeeded = not check_if_database_exists(database, pwd)
    if succeeded is False:
        print("Problem destroying database: {}".format(database))
    elif succeeded is True:
        msg = "Database: {} destroyed.".format(database)
        if backup and backup_to:
            msg += "Data backed up to {}".format(backup_to)
        print(msg)

def destroy_user(user, pwd):
    sql = "DROP USER IF EXISTS {}".format(user)
    db_cxn(sql, pwd)
    succeeded = not check_if_user_exists(user, pwd)
    if succeeded is False:
        print("Problem destroying user: {}".format(user))
    elif succeeded is True:
        print("User: {} destroyed".format(user))

def create_user(user, pwd):
    sql_create_user = "CREATE USER {} WITH PASSWORD '{}';"
    sql_make_superuser = "ALTER ROLE {} WITH SUPERUSER;"
    exists = check_if_user_exists(user, pwd)
    if exists:
        print("User: {} already exists".format(user))
        return
    sql1 = sql_create_user.format(user, pwd)
    db_cxn(sql1, pwd)
    succeeded = check_if_user_exists(user, pwd)
    if succeeded is False:
        print("Problem creating user: {}".format(user))
    else:
        sql2 = sql_make_superuser.format(user, pwd)
        db_cxn(sql2, pwd)
        print("User: {} created".format(user))

def create_database(database, user, pwd):
    sql_createdb = sql_create_db = "CREATE DATABASE {};".format(database, user)
    sql_user_create_db_privilege = "ALTER USER \"{}\" CREATEDB;"
    sql_grant_user_all_db_priv = "GRANT ALL PRIVILEGES ON DATABASE {} TO {};"
    exists = check_if_database_exists(database, pwd)
    if exists:
        print("Database: {} already exists!".format(database))
        migrate()
        return
    db_cxn(sql_user_create_db_privilege, pwd)
    db_cxn(sql_createdb, pwd)
    db_cxn(sql_grant_user_all_db_priv, pwd)
    succeeded = check_if_database_exists(database, pwd)
    if succeeded is False:
        print("Problem creating database: {}".format(database))
    else:
        print("Database: {} created".format(database))
    migrate()
    load_fixtures("initial_settings.yaml")

def prompt(message, default, validate):
    answer = input(message)
    answer = default if answer == '' else answer
    try:
        return validate(answer)
    except:
        print("\n{} is not recognised, try again:\n".format(answer))
        return prompt(message, default, validate)

def run_unit_tests(app=None):
    try:
        if app is None:
            print("Running unit tests")
            run("{}/manage.py test".format(application), pty=True)
        else:
            print("Running functional and unit tests for {}...".format(app))
            run("{}/manage.py test {}".format(application, app), pty=True)
        print('OK')
    except Exception as e:
        print("Some tests failed")

@task
def run_lint_tests():
    print("Running flake8 lint tests...")
    try:
        cmd = "/usr/bin/python3 -m flake8 --exclude={0}/tests/,"
        cmd += "{0}/oilserver/migrations/ {0} --ignore=F403"
        run(cmd.format(application), pty=True)
        print('OK')
    except Exception as e:
        print("Some tests failed")

def run_functional_tests(app=None):
    """While this could and probably should be done as part of 'manage.py test'
    selenium with webdriver for some reason is still not available for Python3.
    As a result, it is being run separately under Python2.
    """
    print("Running functional tests")
    run("python2 {}/tests_functional.py".format(application))

def yes_no(val):
    YES_OR_NO = re.compile("^(y|n|yes|no)$",re.IGNORECASE)
    if YES_OR_NO.match(val):
        return val.lower() == 'y' or val.lower() == 'yes'
    raise Exception("Enter y or n")

def i_am_sure(val):
    return True if val.lower() == "i am sure" else False

def deploy(ipaddr=None, port=None, server="apache"):
    if server == "apache":
        deploy_with_apache(sites_available_location, deploy_path, application)
    else:
        deploy_with_runserver(ipaddr, port)

def deploy_with_runserver(ipaddr, port):
    result = run('{} {}/manage.py runserver {}:{}'.format(preamble,
                 application, ipaddr, port), pty=True)

def deploy_with_apache(apacheconf, deployloc, application, wsgifile="wsgi.py",
                       static_dir="oilserver/static", user_group = "www-data"):
    """Writes apache conf file and restarts the service."""

    with open(setup_file_loc, 'r') as su:
        author_email_list = [admin for admin in su.readlines() if
                             'author_email' in admin]
    pattern = re.compile("<.*>")
    author_email = pattern.findall(str(author_email_list[0]))[0][1:-1]

    a2conf = "ServerName {2}\n"
    a2conf += "LogLevel debug\n"
    a2conf += "\n"
    a2conf += "\n"
    a2conf += "Alias /static {0}/{3}\n"
    a2conf += "<Directory {0}/{3}>\n"
    a2conf += "     Require all granted\n"
    a2conf += "</Directory>\n"
    a2conf += "\n"
    a2conf += "<Directory {0}/{2}>\n"
    a2conf += "    <Files {1}>\n"
    a2conf += "        Require all granted\n"
    a2conf += "    </Files>\n"
    a2conf += "</Directory>\n"
    a2conf += "\n"
    a2conf += "WSGIDaemonProcess weebl user={6} group={6} python-path={0}"
    a2conf += "\n"
    a2conf += "WSGIProcessGroup weebl\n"
    a2conf += "WSGIScriptAlias / {0}/{2}/{1}\n"
    a2conf += "\n"
    a2conf += "ServerAdmin {4}\n"
    a2conf += "ErrorLog {5}/error.log\n"
    a2conf += "CustomLog {5}/access.log combined\n"
    a2conf = a2conf.format(deployloc, wsgifile, application, static_dir,
                           author_email, "${APACHE_LOG_DIR}", user_group)

    with open(apacheconf, 'w') as apache_conf_file:
        print(a2conf, file=apache_conf_file)

    run("sudo apache2ctl -t") # == 'Syntax OK'
    run("sudo a2enmod wsgi") # == "Module wsgi already enabled"
    run("sudo a2ensite weebl.conf") #
    run("sudo service apache2 reload")
    run("sudo service apache2 restart")

def mkdir(directory):
    """ Make a directory, check and throw an error if failed. """
    if not os.path.isdir(directory):
        try:
            os.makedirs(directory)
        except OSError:
            if not os.path.isdir(directory):
                raise

def copy_system_angularjs():
    """Copies Angularjs files from system dir (installed via the install_deps
    script) and copies them to local folder (which is in the gitignore file).
    This obviously assumes that install_deps has been run first.
    """
    mkdir(jslibs_dest_dir)
    for jslibs_js in jslibs_files:
        src = "{}{}".format(jslibs_src_dir, jslibs_js)
        dest = "{}{}".format(jslibs_dest_dir, jslibs_js)
        mkdir(os.path.dirname(dest))
        shutil.copy2(src, dest)
