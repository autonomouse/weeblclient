.PHONY: all
all: run

.PHONY: createuser
createuser:
	tools/create_user

.PHONY: install_deps
install_deps:
	tools/install_deps

.PHONY: syncdb
syncdb: install_deps createuser
	weebl/manage.py syncdb

.PHONY: run
run: syncdb
	tools/run_weebl
