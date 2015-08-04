import utils
from django.db import models
from django.contrib.sites.models import Site
from oilserver.status_checker import StatusChecker
from weebl.__init__ import __api_version__


class WeeblSetting(models.Model):
    """Settings for Weebl"""
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


class Environment(models.Model):
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


class Jenkins(models.Model):
    """The Continuous Integration Server."""
    environment = models.OneToOneField(Environment)
    service_status = models.ForeignKey(ServiceStatus)
    external_access_url = models.URLField(
        unique=True,
        help_text="A URL for external access to this server.")
    internal_access_url = models.URLField(
        unique=True,
        default=None,
        blank=True,
        help_text="A URL used internally (e.g. behind a firewall) for access \
        to this server.")
    service_status_updated_at = models.DateTimeField(
        default=utils.time_now,
        auto_now_add=True,
        help_text="DateTime the service status was last updated.")

    def __str__(self):
        return self.external_access_url

    @property
    def uuid(self):
        return self.environment.uuid


class BuildExecutor(models.Model):
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
        unique=True,
        default=uuid.default,
        help_text="Name of the jenkins build executor.")
    jenkins = models.ForeignKey(Jenkins)


class Pipeline(models.Model):
    """The pipelines currently recorded."""
    uuid = models.CharField(
        max_length=36,
        default=utils.generate_uuid,
        unique=True,
        blank=False,
        null=False,
        help_text="The pipeline ID (a UUID).")
    build_executor = models.ForeignKey(BuildExecutor)


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
