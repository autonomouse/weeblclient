SEG_DASHBOARD = dash.html
ARSENAL_SCRIPTS = ../../scripts
CBD = $(ARSENAL_SCRIPTS)/collect-bug-data

all: reports 
reports: $(SEG_DASHBOARD)

.PHONY: $(SEG_DASHBOARD)
$(SEG_DASHBOARD) :
	$(CBD) --debug=verbose support-engineering.json

