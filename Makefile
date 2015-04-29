.PHONY: all
all: run

.PHONY: createdb
createdb:
	tools/create_db_and_user bugs_database weebl passweebl

.PHONY: create_test_db
createdb:
	tools/create_db_and_user test_bugs_database test_weebl passweebl

.PHONY: install_deps
install_deps:
	tools/install_deps

.PHONY: syncdb
syncdb: install_deps
	weebl/manage.py syncdb

.PHONY: run
run: export DJANGO_SETTINGS_MODULE=weebl.settings
run: createdb syncdb
	tools/run_weebl

.PHONY: test
test: export DJANGO_SETTINGS_MODULE=weebl.test_settings
test: create_test_db syncdb
	tools/run_tests lint
	tools/run_tests unit

.PHONY: destroy_test_vars
destroy_test_vars:
	tools/destroy_user test_bugs_database
	tools/destroy_db test_weebl
