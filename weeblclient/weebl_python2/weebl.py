from warnings import warn
from copy import deepcopy
from six.moves.urllib_parse import urljoin
from weeblclient.weebl_python2.exception import BundleNotAnnotated
from weeblclient.weebl_python2 import utils
from weeblclient.weebl_python2.oldweebl import OldWeebl
from weeblclient.weebl_python2.tastypie_client import Requester, ApiClient

#uri_fields that are not based on uuid
URI_FIELD_OVERRIDES = {
    'servicestatus': 'name',
    'ubuntuversion': 'name',
    'openstackversion': 'name',
    'jobtype': 'name',
    'testcaseinstancestatus': 'name',
    'targetfileglob': 'glob_pattern',
}


class Weebl(object):
    """Weebl API wrapper class.

    This class provides a wrapper around the Python weeblclient REST API and
    includes helper methods to enable easier interaction with the Weebl server.
    """

    def __init__(self, uuid, env_name, username=None, apikey=None,
                 weebl_url="http://10.245.0.14",
                 weebl_api_ver="v1"):
        self.uuid = uuid
        resource_url = "/api/{}/".format(weebl_api_ver)
        base_url = urljoin(weebl_url, resource_url)
        requester = Requester(base_url, username, apikey)
        self.resources = ApiClient(requester, URI_FIELD_OVERRIDES)
        self.oldweebl = OldWeebl(uuid, env_name, username, apikey, weebl_url,
                                 weebl_api_ver)
        self.LOG = utils.get_logger("weeblclient")

    # deprecate oldweebl calls with a warning, so we can track and replace them
    def __getattr__(self, attr):
        if hasattr(self.oldweebl, attr):
            base_attr = getattr(self.oldweebl, attr)
            if hasattr(base_attr, '__call__'):
                warn('Using deprecated Weebl call %s' % attr)
            return base_attr
        else:
            raise AttributeError

    def create_pipeline(self, buildexecutor_name, pipeline_id=None,
                        ubuntuversion_name=None, openstackversion_name=None):
        """Creates a new instance of the 'Pipeline' model.

        Args:
            buildexecutor_name: A required string representing the name of the
                BuildExecutor.
            pipeline_id: An optional UUID string used to identify the pipeline
                may be provided. This will otherwise be auto-generated.
            openstackversion_name: An optional string used to identify the
                version of openstack used.
            ubuntuversion_name: An optional string used to identify the
                version of ubuntu used.

        Returns:
            A string representing the pipeline (this should be the same as the
                one given for pipeline_id).

        Raises:
            Exception: An error will occur if the pipeline given and the
                pipeline returned do not match.

        """
        buildexecutor = self.resources.buildexecutor.get(
            name=buildexecutor_name, jenkins__environment__uuid=self.uuid)

        versionconfiguration = None
        if ubuntuversion_name is not None and openstackversion_name is not None:
            ubuntuversion = self.resources.ubuntuversion.get_or_create(
                name=ubuntuversion_name)
            openstackversion = self.resources.openstackversion.get_or_create(
                name=openstackversion_name)
            versionconfiguration = \
                self.resources.versionconfiguration.get_or_create(
                    ubuntuversion=ubuntuversion,
                    openstackversion=openstackversion)

        return self.resources.pipeline.create(
            uuid=pipeline_id, buildexecutor=buildexecutor,
            versionconfiguration=versionconfiguration)['uuid']

    def get_bug_info(self, force_refresh=True):
        self.LOG.info("Downloading bug regexes from Weebl")
        return utils.munge_bug_info_data(self.resources.knownbugregex.objects())

    def get_job_history(self, environment_uuid, start_date=None):
        params = {
            'pipeline__buildexecutor__jenkins__environment__uuid':
                environment_uuid,
            'count_runs': True,
        }
        if start_date is not None:
            params['pipeline__completed_at__gte'] = start_date

        # slight mangling to get into old format
        choices = []
        for choice in self.resources.configurationchoices.objects(**params):
            runs = choice['runs']
            del choice['runs']
            choices.append([choice['config'], runs])
        return choices

    @staticmethod
    def _check_bundle_annotated(bundle):
        if not bundle:
            return False
        if 'machines' not in bundle:
            return False
        for service_config in bundle['services'].values():
            if 'products' in service_config and service_config['products']:
                return True
        return False


    def push_bundle_info(self, pipeline_id, bundle, require_annotations=False):
        """Push info from a bundle (dict) for the given pipeline_id. The bundle
        can either be annotated with extra data or not. Preferably it will be
        so that all extra data can be propogated. If require_annotations is
        True, then we will check to ensure it is annotated and if not, raise an
        error (BundleNotAnnotated).

        Assuming pipeline is already created remotely.
        """
        bundle = deepcopy(bundle['oil_deployment'])
        annotated = Weebl._check_bundle_annotated(bundle)
        if require_annotations and not annotated:
            raise BundleNotAnnotated('Given bundle is not annotated')

        pipeline = self.resources.pipeline.get(uuid=pipeline_id)
        def actual_machine_name(name):
            """recursively lookup physical machine name for lxcs"""
            lxc_prefix = 'lxc:'
            if name.startswith(lxc_prefix):
                name = name.replace(lxc_prefix, '', 1)
            try:
                service_name, unit = name.split('=')
                name = bundle['services'][service_name]['to'][int(unit)]
                return actual_machine_name(name)
            except (KeyError, ValueError):
                return name

        machineconfigurations = {}
        def push_machineconfiguration(name):
            """create or return machineconfiguration, which links to machine
            and productundertest children. Do as much as possible depending on
            if annotations are given.
            """
            if name in machineconfigurations:
                return machineconfigurations[name]
            hostname = name
            if annotated:
                hostname = bundle['machines'][name].get('host', hostname)
            machine = self.resources.machine.get_or_create(hostname=hostname)
            productundertests_uris = []
            if annotated:
                for product in bundle['machines'][name].get('products'):
                    productundertest = self.resources.productundertest.\
                        get_or_create(name=product)
                    productundertests_uris.append(productundertest.resource_uri)

            machineconfiguration = self.resources.machineconfiguration.create(
                machine=machine,
                productundertests=productundertests_uris)
            machineconfigurations[name] = machineconfiguration
            return machineconfiguration

        def push_jujuservicedeployment(service, config):
            """create jujuservicesdeployment, which links to pipeline, charm.
            jujuservice, productundertest, and unit children -- which may or
            may not have children themselves. Do as much as possible depending
            on if annotations are given.
            """
            jujuservice = self.resources.jujuservice.get_or_create(name=service)
            charm = None
            if 'charm' in config:
                charm = self.resources.charm.get_or_create(
                    name=service, charm_source_url=config['charm'])
            productundertest = None
            if annotated and 'products' in config and config['products']:
                # FIXME: Need ManyToMany jujuservicedeployment <-> PUT
                product = config['products'][0]
                productundertest = \
                    self.resources.productundertest.get_or_create(
                        name=product)
            jujuservicedeployment = self.resources.jujuservicedeployment.create(
                pipeline=pipeline,
                jujuservice=jujuservice,
                charm=charm,
                productundertest=productundertest)
            for number, unit in enumerate(config.get('to', [])):
                machineconfiguration = push_machineconfiguration(
                    actual_machine_name(unit))
                self.resources.unit.create(
                    number=number,
                    jujuservicedeployment=jujuservicedeployment,
                    machineconfiguration=machineconfiguration)

        for service, config in bundle.get('services', {}).items():
            push_jujuservicedeployment(service, config)

        if 'bootstrap' in bundle:
            push_jujuservicedeployment('bootstrap', bundle['bootstrap'])
