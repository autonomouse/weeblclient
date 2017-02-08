from datetime import datetime
from weeblclient.weebl_python2.weebl import Weebl

weebl = Weebl("c7037955-5096-463d-8b3d-fa153da5fffa",
              "cdo-qa", username="JasonHobbs",
              apikey="2e2a0231200985d4ed8fef4d33dcf02c0385b769",
              weebl_url="http://10.204.180.252:8000")

client = weebl.resources

# BuildExecutor is which jenkins slave was used. This has
# to be created somehow. You can do this via the admin
# interface, or via the API. Here we're just using the
# first one.
buildexecutor = list(client.buildexecutor.objects())[0]

# A test run in weebl is a Pipeline.
pipeline = client.pipeline.create(
    buildexecutor=buildexecutor,
    completed_at=datetime.now().isoformat(),
)

print(pipeline)
