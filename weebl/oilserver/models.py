import utils
from django.db import models
from django.contrib.sites.models import Site
from oilserver.status_checker import StatusChecker
from weebl.__init__ import __api_version__


class TimeStampedBaseModel(models.Model):
    """Base model with timestamp information that is common to many models.
    Please note that not all models will inherit from this base model. In
    particular, any that are part of the initial fixtures file do not
    (weeblsetting, servicestatus, buildstatus, and jobtype).
    """

    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        help_text="DateTime this model instance was created.")
    updated_at = models.DateTimeField(
        default=utils.time_now,
        auto_now_add=True,
        help_text="DateTime this model instance was last updated.")

    def save(self, *args, **kwargs):
        current_time = utils.time_now()
        if self.id is None:
            self.created_at = current_time
        self.updated_at = current_time
        return super(TimeStampedBaseModel, self).save(*args, **kwargs)


class WeeblSetting(models.Model):
    """Settings for Weebl."""
    site = models.OneToOneField(
        Site,
        unique=True,
        help_text="To make sure there is only ever one instance per website.")
    check_in_unstable_threshold = models.IntegerField(
        default=300,
        help_text="The time (sec) taken for jenkins to check in, problem \
        suspected if over.")
    check_in_down_threshold = models.IntegerField(
        default=1800,
        help_text="The time (sec) taken for jenkins to check in, definate \
        problem if over.")
    low_build_queue_threshold = models.IntegerField(
        default=3,
        help_text="There are too few builds in queue when lower than this.")
    overall_unstable_th = models.IntegerField(
        default=65,
        help_text="Overall success rate unstable thresholds.")
    overall_down_th = models.IntegerField(
        default=50,
        help_text="Overall success rate down thresholds.")
    down_colour = models.CharField(
        max_length=25,
        default="red",
        help_text="Highlight when warning.")
    unstable_colour = models.CharField(
        max_length=25,
        default="orange",
        help_text="Highlight when unstable.")
    up_colour = models.CharField(
        max_length=25,
        default="green",
        help_text="Highlight when no problems (up).")
    weebl_documentation = models.URLField(
        default=None,
        blank=True,
        help_text="URL to documentation.")

    def __str__(self):
        return str(self.site)

    @property
    def weebl_version(self):
        return utils.get_weebl_version()

    @property
    def api_version(self):
        return __api_version__


class Environment(TimeStampedBaseModel):
    """The environment (e.g. Prodstack, Staging)."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of environment.")
    name = models.CharField(
        max_length=255,
        unique=True,
        default=uuid.default,
        blank=True,
        null=True,
        help_text="Name of environment.")

    def __str__(self):
        return "{} ({})".format(self.name, self.uuid)

    def get_set_go(self):
        current_site = Site.objects.get_current().id
        return WeeblSetting.objects.get(pk=current_site)

    @property
    def state_description(self):
        status_checker = StatusChecker(self.get_set_go())
        return status_checker.get_current_oil_situation(self, ServiceStatus)

    @property
    def state(self):
        status_checker = StatusChecker(self.get_set_go())
        return status_checker.get_current_oil_state(self, ServiceStatus)

    @property
    def state_colour(self):
        return getattr(self.get_set_go(), '{}_colour'.format(self.state))


class ServiceStatus(models.Model):
    """Potential states that the CI server (Jenkins) may be in (e.g. up,
    unstable, down, unknown).
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        default="unknown",
        help_text="Current state of the environment.")
    description = models.TextField(
        default=None,
        blank=True,
        null=True,
        help_text="Optional description for status.")

    def __str__(self):
        return self.name


class Jenkins(TimeStampedBaseModel):
    """The Continuous Integration Server."""
    environment = models.OneToOneField(Environment)
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of the jenkins instance.")
    service_status = models.ForeignKey(ServiceStatus)
    external_access_url = models.URLField(
        unique=True,
        help_text="A URL for external access to this server.")
    internal_access_url = models.URLField(
        unique=True,
        default=None,
        blank=True,
        null=True,
        help_text="A URL used internally (e.g. behind a firewall) for access \
        to this server.")
    service_status_updated_at = models.DateTimeField(
        default=utils.time_now,
        auto_now_add=True,
        help_text="DateTime the service status was last updated.")

    def __str__(self):
        return self.external_access_url


class BuildExecutor(TimeStampedBaseModel):
    """The Jenkins build executor (master or slave)."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of the jenkins build executor.")
    name = models.CharField(
        max_length=255,
        help_text="Name of the jenkins build executor.")
    jenkins = models.ForeignKey(Jenkins)

    class Meta:
        # Jenkins will default to naming the build_executers the same thing
        # (e.g. 'master, 'ci-oil-slave-10-0', etc) so while they must be unique
        # within the same environment/jenkins, they will only be unique when
        # combined with the environment/jenkins uuid, externally:
        unique_together = (('name', 'jenkins'),)

        # Order the build executors so they are printed in alphabetical order:
        ordering = ['name']

    def __str__(self):
        return self.uuid


class UbuntuVersion(models.Model):
    """The version of the Ubuntu operating system in a pipeline."""
    name = models.CharField(
        max_length=255,
        unique=True,
        default="",
        help_text="The name of the version of the Ubuntu system.")
    number = models.CharField(
        max_length=10,
        unique=True,
        default="",
        help_text="The numerical version of the Ubuntu system")

    def __str__(self):
        return self.name


class OpenstackVersion(models.Model):
    """The version of OpenStack running in a pipeline."""
    name = models.CharField(
        max_length=255,
        unique=True,
        default="unknown",
        help_text="The name of the version of the OpenStack system.")

    def __str__(self):
        return self.name


class SDN(models.Model):
    """The type of SDN being used in a pipeline."""
    name = models.CharField(
        max_length=255,
        unique=True,
        default="unknown",
        help_text="The name of the software defined network.")

    def __str__(self):
        return self.name


class Compute(models.Model):
    """The type of Compute being used in a pipeline."""
    name = models.CharField(
        max_length=255,
        unique=True,
        default="unknown",
        help_text="The name of the Compute type.")

    def __str__(self):
        return self.name


class BlockStorage(models.Model):
    """The type of Block Storage being used in a pipeline."""
    name = models.CharField(
        max_length=255,
        unique=True,
        default="unknown",
        help_text="The name of the Block Storage type.")

    def __str__(self):
        return self.name


class ImageStorage(models.Model):
    """The type of Image Storage being used in a pipeline."""
    name = models.CharField(
        max_length=255,
        unique=True,
        default="unknown",
        help_text="The name of the Image Storage type.")

    def __str__(self):
        return self.name


class Database(models.Model):
    """The type of Database being used in a pipeline."""
    name = models.CharField(
        max_length=255,
        unique=True,
        default="unknown",
        help_text="The name of the Database type.")

    def __str__(self):
        return self.name


class Pipeline(TimeStampedBaseModel):
    """The pipelines currently recorded."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="The pipeline ID (a UUID).")
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        default=None,
        auto_now_add=False,
        help_text="DateTime the pipeline was completed.")
    ubuntu_version = models.ForeignKey(
        UbuntuVersion, null=True, blank=True, default=None)
    openstack_version = models.ForeignKey(
        OpenstackVersion, null=True, blank=True, default=None)
    sdn = models.ForeignKey(SDN, null=True, blank=True, default=None)
    compute = models.ForeignKey(Compute, null=True, blank=True, default=None)
    block_storage = models.ForeignKey(BlockStorage, null=True, blank=True,
                                      default=None)
    image_storage = models.ForeignKey(ImageStorage, null=True, blank=True,
                                      default=None)
    database = models.ForeignKey(Database, null=True, blank=True, default=None)
    build_executor = models.ForeignKey(BuildExecutor)

    def __str__(self):
        return self.uuid


class BuildStatus(models.Model):
    """Potential states that the build may be in following being run on the CI
    server (Jenkins; e.g. success, failure, aborted, unknown).
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        default="unknown",
        help_text="The resulting state of the build.")
    description = models.TextField(
        default=None,
        blank=True,
        null=True,
        help_text="Optional description for state.")

    def __str__(self):
        return self.name


class JobType(models.Model):
    """The type of job run (e.g. pipeline_deploy, pipeline_prepare,
    test_tempest_smoke).
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        default="pipeline_deploy",
        help_text="The type of job.")
    description = models.TextField(
        default=None,
        blank=True,
        null=True,
        help_text="Optional description of job type.")

    def __str__(self):
        return self.name


class Build(TimeStampedBaseModel):
    """The build numbers for each job."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this build.")
    build_id = models.CharField(
        max_length=255,
        help_text="The build number or other identifier used by jenkins.")
    artifact_location = models.URLField(
        default=None,
        null=True,
        unique=True,
        help_text="URL where build artifacts can be obtainedIf archived, then \
        jenkins has been wiped and the build numbers reset, so this data is \
        no longer accessble via jenkins link")
    build_started_at = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        help_text="DateTime the build was started.")
    build_finished_at = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        help_text="DateTime the build finished.")
    build_analysed_at = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        help_text="DateTime build analysed by weebl, or None if unanalysed.")
    pipeline = models.ForeignKey(Pipeline)
    build_status = models.ForeignKey(BuildStatus)
    job_type = models.ForeignKey(JobType)

    def __str__(self):
        return self.uuid

class TargetFileGlob(TimeStampedBaseModel):
    """The target file."""
    glob_pattern = models.TextField(
        unique=True,
        help_text="Glob pattern used to match one or more target files.")
    job_types = models.ManyToManyField(
        JobType, null=True, blank=True, default=None)

    def __str__(self):
        return self.glob_pattern


class Project(TimeStampedBaseModel):
    """A system for tracking bugs (e.g. Launchpad). """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of project.")

    def __str__(self):
        return self.name


class BugTrackerBug(TimeStampedBaseModel):
    """An error that has resulted in an incorrect or unexpected behaviour or
    result, externally recorded on a bug-tracker (such as Launchpad).
    """
    bug_number = models.IntegerField(
        unique=True,
        blank=False,
        null=False,
        help_text="Designation of this bug (e.g. Launchpad bug number).")
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this bug.")
    project = models.ForeignKey(Project, null=True, blank=True, default=None)

    def __str__(self):
        return self.uuid


class Bug(TimeStampedBaseModel):
    """An error in OIL that has resulted in an incorrect or unexpected
    behaviour or result.
    """
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this bug.")
    summary = models.CharField(
        max_length=255,
        unique=True,
        default=uuid.default,
        help_text="Brief overview of bug.")
    description = models.TextField(
        default=None,
        blank=True,
        null=True,
        help_text="Full description of bug.")
    bug_tracker_bug = models.OneToOneField(
        BugTrackerBug,
        help_text="Bug tracker bug associated with this bug.",
        blank=True,
        null=True,
        default=None)

    def __str__(self):
        return self.uuid


class KnownBugRegex(TimeStampedBaseModel):
    """The regex used to identify a bug."""
    bug = models.ForeignKey(Bug, null=True, blank=True, default=None)
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this pattern.")
    # While regex must be unique, it can be set to multiple target files:
    regex = models.TextField(
        unique=True,
        help_text="The regular expression used to identify a bug occurrence.")
    target_file_globs = models.ManyToManyField(TargetFileGlob)

    def __str__(self):
        return self.uuid


class BugOccurrence(TimeStampedBaseModel):
    """The occurrence of a bug."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="UUID of this bug occurrence.")
    build = models.ForeignKey(Build)
    regex = models.ForeignKey(KnownBugRegex)

    class Meta:
        # Only create one BugOccurrence instance per build/regex combo:
        unique_together = (('build', 'regex'),)

    def __str__(self):
        return self.uuid
