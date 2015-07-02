#!/usr/bin/env python3
import os
import re
import sys
import psycopg2
import psutil
from invoke import task, run

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
test_ipaddr = '127.0.0.1'
prdctn_ipaddr = '127.0.0.1'
test_port = '8001'
prdctn_port = '8000'
sites_available_location = "/etc/apache2/sites-available/weebl.conf"
file_loc = os.path.dirname(os.path.abspath(__file__))
deploy_path = "{}/{}".format(file_loc, application)  # change
setup_file_loc = "setup.py"

''' REQUIRES install_deps to have been run first. '''

@task(default=True)
def list():
    """List all available tasks."""
    run("invoke --list")
    run('invoke --help')

@task(help={'database': "Type test or production",
			'server': "Optionally suffix with -s runserver",})
def go(database, server="apache"):
    """Set up and run weebl using either a test or a production database."""
    initialise_database(database)
    deploy(prdctn_ipaddr, prdctn_port, server)

@task
def run_tests():
    """Run unit, functional, and lint tests for each app."""
    for app in apps:
        run_unit_tests(app)
    run_lint_tests()

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
                print("Failed to kill {} process id {}. Exception: {}"
                      .format(proc.name(), proc.pid, e))

@task(help={'database': "Type test or production"})
def destroy(database):
    """Destroy either the test or production database and user."""
    if database == "production":
        destroy_production_data()
    elif database == "test":
        destroy_test_data()

def initialise_database(database):
    if database == "production":
        stngs = prdctn_settings
        user = prdctn_user
        port = prdctn_port
    elif database == "test":
        stngs = test_settings
        ipaddr = test_user
        port = test_port
    else:
        print("Please provide an option: either 'production' or 'test'")
        return
    set_postgres_password(postgres_pwd)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{0}.{1}"
                          .format(application, stngs))
    createdb(database)

def migrate():
    """Make migrations and migrate."""
    run("{}/manage.py makemigrations".format(application))
    run("{}/manage.py migrate".format(application))

def create_production_db():
    create_db_and_user(prdctn_db_name, prdctn_user, prdctn_pwd)

def create_test_db():
    create_db_and_user(test_db_name, test_user, test_pwd)

def migrate_individual_app(application, app):
    print("Migrating '{}'".format(app))
    run('{}/manage.py makemigrations {}'.format(application, app))
    run('{}/manage.py migrate {}'.format(application, app))

def destroy_test_data():
    rusure = "Are you sure you want to drop the test database and user?! (y/N)"
    if prompt(rusure, default='N', validate=yes_no):
        destroy_db(test_db_name, test_pwd)
        destroy_user(test_user, test_pwd)

def destroy_production_data():

    # TODO: Offer to back up the database first!!!

    rusure1 = "You want to drop the PRODUCTION database (y/N)"
    rusure1 += " - are you absolutely sure about that?! (y/N)"
    rusure2 = "Really? I'll only ask one more time after this!!! (y/N)"
    rusure3 = "I don't believe you. Call me paranoid, but this is PRODUCTION "
    rusure3 += "data we're talking about! Type \"I am sure\" to proceed:\n>"
    rusure4 = "Are you sure you want to drop the user: {}?! (y/N)"

    if prompt(rusure1, default='N', validate=yes_no):
        if prompt(rusure2, default='N', validate=yes_no):
            if prompt(rusure3, default='N', validate=i_am_sure):
                destroy_db(prdctn_db_name, prdctn_pwd)
                user = prdctn_user
                if prompt(rusure4.format(user), default='N', validate=yes_no):
                    destroy_user(prdctn_user, prdctn_pwd)
                else:
                    print("User deletion aborted")
                return
    print("Phew - that was close...")

def create_db_and_user(db_name, user, pwd):
    create_user(user, pwd)
    create_db(db_name, user, pwd)

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

def destroy_db(database, pwd):
    sql = "DROP DATABASE IF EXISTS {}".format(database)
    db_cxn(sql, pwd)
    succeeded = not check_if_database_exists(database, pwd)
    if succeeded is False:
        print("Problem destroying database: {}".format(database))
    elif succeeded is True:
        print("Database: {} destroyed".format(database))

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

def create_db(database, user, pwd):
    sql_createdb = sql_create_db = "CREATE DATABASE {};".format(database, user)
    sql_user_create_db_privilege = "ALTER USER \"{}\" CREATEDB;"
    sql_grant_user_all_db_priv = "GRANT ALL PRIVILEGES ON DATABASE {} TO {};"
    exists = check_if_database_exists(database, pwd)
    if exists:
        print("Database: {} already exists!".format(database))
        syncdb()
        return
    db_cxn(sql_user_create_db_privilege, pwd)
    db_cxn(sql_createdb, pwd)
    db_cxn(sql_grant_user_all_db_priv, pwd)
    succeeded = check_if_database_exists(database, pwd)
    if succeeded is False:
        print("Problem creating database: {}".format(database))
    else:
        print("Database: {} created".format(database))
    syncdb()
    load_fixtures("initial_settings.yaml")

def prompt(message, default, validate):
    answer = input(message)
    try:
        return validate(answer)
    except:
        print("\n{} is not recognised, try again:\n".format(answer))
        return prompt(message, default, validate)

def run_unit_tests(app=None):
    try:
        if app is None:
            print("Running functional and unit tests")
            run("{}/manage.py test".format(application), pty=True)
        else:
            print("Running functional and unit tests for {}...".format(app))
            run("{}/manage.py test {}".format(application, app), pty=True)
        print('OK')
    except Exception as e:
        print("Some tests failed")

def run_lint_tests():
    print("Running flake8 lint tests...")
    try:
        run("/usr/bin/python3 -m flake8 --exclude {0}/tests/ {0} --ignore=F403"
            .format(application), pty=True)
        print('OK')
    except Exception as e:
        print("Some tests failed")

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

def load_fixtures(fixture):
    print("Adding data from {} into database".format(fixture))
    run('{}/manage.py loaddata "{}"'.format(application, fixture))

def deploy_with_apache(apacheconf, deployloc, application, wsgifile="wsgi.py",
					   static_dir="oilserver/static", user_group = "www-data"):
    """Writes apache conf file and restarts the service."""

    with open(setup_file_loc, 'r') as su:
        author_email_list = [admin for admin in su.readlines() if
                             'author_email' in admin]
    pattern = re.compile("<.*>")
    author_email = pattern.findall(str(author_email_list))[0][1:-1]

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
