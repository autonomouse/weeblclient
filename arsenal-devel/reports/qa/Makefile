REPORT_HOST = cranberry.canonical.com
REPORT_ROOT = /srv/qa.ubuntu.com/reports/kernel-bugs/reports/
ONEIRIC_MILESTONE_BUGS_REPORT = oneiric-milestone-bugs.html
PRECISE_MILESTONE_BUGS_REPORT = precise-milestone-bugs.html
PRECISE_ISO_TESTING_REPORT = precise-iso-testing.html
ISO_TESTING_BUGS_REPORT = iso-testing-open-all.html
RESOURCES = ../cached-lp-resources.json
ARSENAL_SCRIPTS = ../../scripts
ARSENAL_TEMPLATES = ../../web/templates
CBD = $(ARSENAL_SCRIPTS)/collect-bug-data
RPT = $(ARSENAL_SCRIPTS)/reporter

all: reports publish
reports: $(PRECISE_MILESTONE_BUGS_REPORT)

$(RESOURCES):
	$(ARSENAL_SCRIPTS)/cache-lp-resources $(RESOURCES)

.PHONY: $(ONEIRIC_MILESTONE_BUGS_REPORT) $(RESOURCES)
$(ONEIRIC_MILESTONE_BUGS_REPORT) :
	$(CBD) --cached-lp-resources=$(RESOURCES) iso-testing-open-oneiric.json
	$(RPT) --title="Oneiric Milestone Bugs" --template=$(ARSENAL_TEMPLATES)/bugs-by-team.mako iso-testing-open-oneiric.json > $@

.PHONY: $(PRECISE_ISO_TESTING_REPORT) $(RESOURCES)
$(PRECISE_ISO_TESTING_REPORT) :
	$(CBD) --cached-lp-resources=$(RESOURCES) iso-testing-open-precise.json
	$(RPT) --title="Precise Iso Testing Bugs" --template=$(ARSENAL_TEMPLATES)/bugs-by-team.mako iso-testing-open-precise.json > $@

.PHONY: $(PRECISE_MILESTONE_BUGS_REPORT) $(RESOURCES)
$(PRECISE_MILESTONE_BUGS_REPORT) :
	$(CBD) --cached-lp-resources=$(RESOURCES) precise-milestone-bugs.json
	$(RPT) --title="Precise Milestone Bugs" --template=$(ARSENAL_TEMPLATES)/bugs-by-team.mako precise-milestone-bugs.json > $@

.PHONY: $(ISO_TESTING_BUGS_REPORT) $(RESOURCES)
$(ISO_TESTING_BUGS_REPORT) :
	$(CBD) --cached-lp-resources=$(RESOURCES) iso-testing-open-all.json
	$(RPT) --title="ISO Testing Bugs" --template=iso-testing-report.mako iso-testing-open-all.json > $@

upload:
	scp iso-testing-open-all.json $(ISO_TESTING_BUGS_REPORT) $(REPORT_HOST):$(REPORT_ROOT)
	scp iso-testing-open-oneiric.json $(ONEIRIC_MILESTONE_BUGS_REPORT) $(REPORT_HOST):$(REPORT_ROOT)

publish:
	scp precise-milestone-bugs.json $(PRECISE_MILESTONE_BUGS_REPORT) $(REPORT_ROOT)
