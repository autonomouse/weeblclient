APPNAME=arsenal
APPURL=http://launchpad.net/arsenal

all: reports

reports:
	cd reports && $(MAKE) data
	cd reports && $(MAKE) html

# Run all the tests
check:
	./run-tests

clean:
	rm -rf doc/api
	find . -name '*.pyc' -print0 | xargs -0 rm -f
	find . -name '*~' -print0 | xargs -0 rm -f

# Check for common & easily catchable Python mistakes.
pyflakes:
	pyflakes $(APPNAME)

# Check for coding standard violations.
pep8:
	find . -name '*.py' -print0 | xargs -0 pep8 --ignore E221,E222
	find . -name '*.py' -print0 | xargs -0 pep8 --ignore E221,E222 --repeat | wc -l

apidocs:
	pydoctor --add-package $(APPNAME) \
		--make-html --html-output=doc/api \
		--project-name=$(APPNAME) \
		--project-url=$(APPURL)

lint: pyflakes pep8

.PHONY: reports check lint pyflakes pep8 apidocs clean

# Ignore pyflakes exit code so pep8 will run for 'make lint'
.IGNORE: pyflakes
