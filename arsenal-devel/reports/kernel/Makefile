REPORT_HOST = cranberry.canonical.com
REPORT_ROOT = /srv/qa.ubuntu.com/reports/kernel-bugs/reports/
RLS_TRACKING = kernel-release-tracking-bugs
RLS_TRACKING_REPORT = $(RLS_TRACKING).html
ARSENAL_SCRIPTS = ../../scripts

all: reports publish
reports: $(RLS_TRACKING_REPORT)

$(RESOURCES):
	$(ARSENAL_SCRIPTS)/cache-lp-resources ../cached-lp-resources.json

.PHONY : $(RLS_TRACKING_REPORT)
$(RLS_TRACKING_REPORT) : $(RESOURCES)
	$(ARSENAL_SCRIPTS)/collect-project-bug-data $(RLS_TRACKING).json
	$(ARSENAL_SCRIPTS)/reporter --title="Kernel Release Tracking Bugs" --template=kernel-release-tracking-bugs.mako $(RLS_TRACKING).json > $@

upload:
	-scp *.json *.html $(RLS_TRACKING_REPORT) $(REPORT_HOST):$(REPORT_ROOT)

publish:
	-scp *.json *.html $(RLS_TRACKING_REPORT) $(REPORT_ROOT)
