(To do: Document the project here the run pandoc README.rst -o README.html)

Initial set up
==============

The tests will not work until you have set up a database on your machine for it to connect to

Install Postgres
sudo apt-get install postgresql
sudo apt-get install python3-psycopg2

sudo su - postgres

createdb bugs_database
createuser user -P
psql
GRANT ALL PRIVILEGES ON DATABASE bugs_database TO "user";
ALTER USER "user" CREATEDB;
createdb bugs_database

exit (Cntl-D) and exit

then 

weebl/manage.py syncdb

Install selenium
sudo pip3 install selenium 
(This may be an issue if the apt-get version doesn't work as its supposed to...)

Run tests using:
./run_tests.sh unit
