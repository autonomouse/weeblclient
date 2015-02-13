REPORT_HOST = cranberry.canonical.com
REPORT_ROOT = /srv/qa.ubuntu.com/reports/kernel-bugs/reports/
RLS_MGR_L_MILESTONE_REPORT = rls-mgr-l-tracking-bugs.html
RLS_MGR_O_MILESTONE_REPORT = rls-mgr-o-tracking-bugs.html
RLS_MGR_P_MILESTONE_REPORT = rls-mgr-p-tracking-bugs.html
RLS_P_TRACKING_MILESTONE_REPORT = rls-p-tracking-bugs.html
RESOURCES = ../cached-lp-resources.json
ARSENAL_SCRIPTS = ../../scripts
ARSENAL_TEMPLATES = ../../web/templates
CBD = $(ARSENAL_SCRIPTS)/collect-bug-data --quiet --cached-lp-resources=../cached-lp-resources.json 
RPT = $(ARSENAL_SCRIPTS)/reporter

all: $(RESOURCES) reports publish
reports: lucid oneiric precise p-tracking o-teams p-teams precise-teams

lucid: $(RLS_MGR_L_MILESTONE_REPORT)
oneiric: $(RLS_MGR_O_MILESTONE_REPORT)
precise: $(RLS_MGR_P_MILESTONE_REPORT)
p-tracking: $(RLS_P_TRACKING_MILESTONE_REPORT)

$(RESOURCES): ../package-team-mapping.csv
	$(ARSENAL_SCRIPTS)/cache-lp-resources --csv=../package-team-mapping.csv ../cached-lp-resources.json

.PHONY : $(RLS_MGR_L_MILESTONE_REPORT)
$(RLS_MGR_L_MILESTONE_REPORT) : $(RESOURCES)
	$(CBD) rls-mgr-l-tracking.json
	$(RPT) --title="Release Mgr. Lucid Tracking Bugs" --template=$(ARSENAL_TEMPLATES)/bugs-by-team.mako rls-mgr-l-tracking.json > $@

.PHONY : $(RLS_MGR_O_MILESTONE_REPORT)
$(RLS_MGR_O_MILESTONE_REPORT) : $(RESOURCES)
	$(CBD) rls-mgr-o-tracking.json
	$(RPT) --title="Release Mgr. Oneiric Tracking Bugs" --template=$(ARSENAL_TEMPLATES)/bugs-by-team.mako rls-mgr-o-tracking.json > $@

o-teams:
	for team in `$(ARSENAL_SCRIPTS)/list-teams rls-mgr-o-tracking.json`;do \
	    $(RPT) --team=$$team --title="Relase Mgr. Oneiric Tracking Bugs - $$team" --template=$(ARSENAL_TEMPLATES)/bugs-by-team.mako rls-mgr-o-tracking.json > rls-mgr-o-tracking-$$team-bugs.html; \
	done

.PHONY : $(RLS_MGR_P_MILESTONE_REPORT)
$(RLS_MGR_P_MILESTONE_REPORT) : $(RESOURCES)
	$(CBD) rls-mgr-p-tracking.json
	$(RPT) --title="Release Mgr. Precise Tracking Bugs" --template=$(ARSENAL_TEMPLATES)/bugs-by-team.mako rls-mgr-p-tracking.json > $@

p-teams:
	for team in `$(ARSENAL_SCRIPTS)/list-teams rls-mgr-p-tracking.json`;do \
	    $(RPT) --team=$$team --title="Relase Mgr. Precise Tracking Bugs - $$team" --template=$(ARSENAL_TEMPLATES)/bugs-by-team.mako rls-mgr-p-tracking.json > rls-mgr-p-tracking-$$team-bugs.html; \
	done

.PHONY : $(RLS_P_TRACKING_MILESTONE_REPORT)
$(RLS_P_TRACKING_MILESTONE_REPORT) : $(RESOURCES)
	$(CBD) rls-p-tracking.json
	$(RPT) --title="Precise Release Tracking Bugs" --template=$(ARSENAL_TEMPLATES)/bugs-by-team.mako rls-p-tracking.json > $@

precise-teams:
	for team in `$(ARSENAL_SCRIPTS)/list-teams rls-mgr-p-tracking.json`;do \
	    $(RPT) --team=$$team --title="Precise Tracking Bugs - $$team" --template=$(ARSENAL_TEMPLATES)/bugs-by-team.mako rls-p-tracking.json > rls-p-tracking-$$team-bugs.html; \
	done

upload:
	-scp *.json *.html $(RLS_MGR_O_MILESTONE_REPORT) $(REPORT_HOST):$(REPORT_ROOT)

publish:
	-scp *.json *.html $(RLS_MGR_O_MILESTONE_REPORT) $(REPORT_ROOT)
