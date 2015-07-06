import os
import json
import yaml
import utils
import pytz
from django.contrib.sites.models import Site
from __init__ import __version__
from collections import namedtuple
from oilserver.models import (
    WeeblSetting,
    Environment,
    ServiceStatus,
    Jenkins
    )

class StatusChecker():
    """ """

    def __init__(self, ):
        if repr(WeeblSetting.objects.all()) == '[]':
            raise Exception("No current site - fixtures must be loaded first!")
        self.current_site = Site.objects.get_current().id
        self.weebl_setting = WeeblSetting.objects.get(pk=self.current_site)


    def get_site_settings(self):
        """Fetches site settings for this site from the database."""
        settings = self.weebl_setting
        sset = {}
        sset['site_id'] = settings.site_id
        sset['check_in_unstable_threshold'] = \
            settings.check_in_unstable_threshold
        sset['check_in_down_threshold'] = settings.check_in_down_threshold
        sset['low_build_queue_threshold'] = settings.low_build_queue_threshold
        sset['overall_unstable_th'] = settings.overall_unstable_th
        sset['overall_down_th'] = settings.overall_down_th
        sset['down_colour'] = settings.down_colour
        sset['unstable_colour'] = settings.unstable_colour
        sset['up_colour'] = settings.up_colour
        sset['weebl_documentation'] = settings.weebl_documentation
        sset['site_name'] = self.current_site

        sset['weebl_version'] = __version__
        return sset


    def get_current_oil_state(self, environment, env=None):
        """Load up report status"""
        if env is None:
            env = namedtuple('env', '')
        env.oil_state = 'up'
        key = '{}_colour'.format(env.oil_state)
        env.oil_state_colour = self.get_site_settings()[key]
        
        import pdb;pdb.set_trace()

        env.oil_situation = []
        #status = environment.current_situation

        delta, time_msg = self.calc_time_since_last_checkin(jenkins.service_status_updated_at)

        self.change_state_if_overdue(delta, env, time_msg)
        #self.change_state_if_dead_nodes(status, env) # <- expects status to be a dict
        #self.change_state_if_too_few_builds(status, env) # <- expects status to be a dict
        self.change_state_if_hanging(env)
        self.change_state_if_queue_stopped(env)
        return env


    def calc_time_since_last_checkin(self, timestamp):
        if timestamp is None:
            return (None,
                    "It is not known how long since Jenkins last checked in")
        # Work out how long it's been since it last checked in:
        time_difference = utils.time_since(timestamp)
        delta = round(time_difference.total_seconds())
        seconds = time_difference.seconds
        minutes = round(seconds / 60)
        hours = round(minutes / 60)
        days = time_difference.days
        weeks = round(days / 7)

        msg = "Jenkins has not checked in for over {} {}"
        if weeks > 0:
            timestr = 'weeks' if weeks > 1 else 'week'
            time_msg = msg.format(weeks, timestr)
        elif days > 0:
            timestr = 'days' if days > 1 else 'day'
            time_msg = msg.format(days, timestr)
        elif hours > 0:
            timestr = 'hours' if hours > 1 else 'hour'
            time_msg = msg.format(hours, timestr)
        else:
            timestr = 'minutes' if minutes > 1 else 'minute'
            time_msg = msg.format(minutes, timestr)
        return (delta, time_msg)


    def change_state_if_overdue(self, delta, env, time_msg):
        unstable_th = self.get_site_settings()['check_in_unstable_threshold']
        down_th = self.get_site_settings()['check_in_unstable_threshold']
        errstate = None
        if delta is None or delta > float(down_th):
            errstate = 'down'
        elif delta > float(unstable_th):
            errstate = 'unstable'
        if errstate:
            self.set_oil_state(env, errstate, time_msg)


    def change_state_if_dead_nodes(self, status, env):
        """Determine if there are any dead nodes"""
        body_count = len(status['dead_nodes'])
        if body_count > 0:
            msg = "The following {} nodes are reported as dead: {}"
            msg = msg.format(body_count, ", ".join(status['dead_nodes']))
            self.set_oil_state(env, 'unstable', msg)


    def change_state_if_too_few_builds(self, status, env):
        """Determine if there are too few builds in the queue"""
        builds_in_q = len(status['start_builds_queue'])
        build_q_th = self.get_site_settings()['low_build_queue_threshold']
        if builds_in_q < int(build_q_th):
            msg = "There are only {} pipeline_start builds currently in the queue"
            self.set_oil_state(env, 'unstable', msg.format(builds_in_q))


    def change_state_if_hanging(self, env):
        """Determine if there are any builds that are hanging"""
        pass  # TODO - not yet implemented on jenkins


    def change_state_if_queue_stopped(self, env):
        """Determine if the Queue Daemon has stopped"""
        pass  # TODO - not yet implemented on jenkins


    def set_oil_state(self, env, new_state, msg):
        # Set state:
        if env.oil_state != 'down':
            env.oil_state = new_state

        # Set colour:
        key = '{}_colour'.format(env.oil_state)
        env.oil_state_colour = self.get_site_settings()[key]

        # Set message:
        if msg != '':
            env.oil_situation.append(msg)
        return env.oil_state

    def get_bug_ranking_data(self, tframe, limit=None):
        """Load up bug_ranking data."""
        tframe.rankings = {}

        # TODO: So here we need to work out which pipelines ran in the given
        # timeframe based on their started/completed/analysed date.
        # Then we need to work out what errors each pipeline has (based on:
        # error -> signature -> build -> job -> pipeline

        '''
        for jobname, yaml_file in bug_ranking_files.items():
            job_ranking = self.load_from_yaml_file(os.path.join(data_location,
                                                           yaml_file))
            job_ranking = dict(job_ranking) if job_ranking else {}

            bugs = [ranking for ranking in job_ranking.items()]

            # Sort bugs by number of hits:
            sorted_bugs = sorted(bugs, key=operator.itemgetter(1), reverse=True)
            tframe.rankings[jobname] = job_ranking
            sorted_bugs = sorted_bugs[:limit] if limit is not None else sorted_bugs
            tframe.rankings[jobname] = sorted_bugs
        '''
        return tframe


    def get_common_data(self, time_range='daily', limit=None):
        """Get all relevant data."""
        launchpad = Launchpad()
        data = namedtuple('data', '')
        data.title = 'weebl'

        # Get settings from database:
        data.env = {}
        self.envrionments = self.environment.objects.all()
        for environment in self.envrionments:
            env_name = environment.name
            data.env[env_name] = namedtuple('env', '')
            data.env[env_name].uuid = environment.uuid
            data.env[env_name].name = env_name
            data.env[env_name].tframe = namedtuple('tframe', '')
            data.env[env_name] = self.get_current_oil_state(
                environment, data.env[env_name])
            tframe = data.env[env_name].tframe
            tframe = self.get_bug_ranking_data(tframe, limit)
            tframe, data.categories, data.breakdown =\
                launchpad.merge_with_launchpad_data(tframe)
        data.settings = self.get_site_settings()
        return data


class Launchpad():
    """ """
    def get_launchpad_data(self):

        # TODO: Pull data from launchpad.
        # First I need to put auth keys in the settings table though

        data_location = os.path.dirname(os.path.abspath(os.path.join(__file__, '../../')))
        file_location = os.path.join(data_location, 'data/OIL.json')

        if not os.path.exists(file_location):
            raise AbsentYamlError("{} missing".format(file_location))

        with open(file_location, 'r') as lp_file:
            return yaml.load(lp_file)

    def merge_with_launchpad_data(self, tframe):
        lp_data = self.get_launchpad_data()
        cats = {}
        bug_cats = {}

        for job, job_ranking in tframe.rankings.items():
            for idx, (bug, hits) in enumerate(job_ranking):
                bug_data = lp_data['tasks'].get(bug)
                if bug_data:
                    bug_data = bug_data[0]
                    lp_link = \
                        os.path.join(cfg.get(MODE, 'launchpad_bugs_url'), bug)
                    assignee = bug_data['assignee']
                    age_days = bug_data['bug']['age_days']
                    date_assigned = bug_data['date_assigned']
                    title = bug_data['bug']['title']
                    importance = bug_data['importance']
                    status = bug_data['status']
                    all_tags = bug_data['bug']['tags']
                else:
                    lp_link = None
                    assignee = ''
                    age_days = ''
                    date_assigned = ''
                    title = ''
                    importance = ''
                    status = ''
                    all_tags = ''
                cats, bug_cats = self.link_tags_with_hi_lvl_categories(cats, all_tags,
                                                                  tframe, job, bug,
                                                                  bug_cats)
                category = bug_cats.get(bug)
                tframe.rankings[job][idx] = (bug, lp_link, hits, lp_link, title,
                                             assignee, age_days, cats,
                                             importance, status, date_assigned,
                                             all_tags, category)
        breakdown = {}
        for category in cats:
            breakdown[category] = len(cats[category])
        # Sort bugs by number of eachcategory:
        # breakdown = sorted(breakdown, key=operator.itemgetter(1), reverse=True)
        return (tframe, cats, breakdown)


    def link_tags_with_hi_lvl_categories(self, categories, all_tags, tframe, job,
                                         bug_id, bug_cats):
        for bug in tframe.rankings[job]:
            if bug[0] == bug_id:
                category = ['Unknown']
                for tag in all_tags:
                    if 'category-' in tag:
                        category = [tag.replace('category-', '')]
                        bug_cats[bug_id] = category
                for cat in category:
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(bug_id)
        return (categories, bug_cats)


class TmpClass():
    """ """

    def get_oil_stats(self, tframe):
        """Load up oilstats"""

        # TODO: Calculate this from data in the database
        oil_stats = None

        #try:
        #    oil_stats = \
        #        self.load_from_yaml_file(os.path.join(data_location, 'oil-stats.yaml'))
        #except AbsentYamlError:
        #    oil_stats = {'jobs': {'pipeline_deploy': {'success rate': '?'},
        #                          'pipeline_prepare': {'success rate': '?'},
        #                          'test_tempest_smoke': {'success rate': '?'}},
        #                 'overall': {'success rate': '?',
        #                             'tempest builds': '?',
        #                             'total jobs': '?'}}
        if not oil_stats:
            return tframe
        SRate = oil_stats['overall']['success rate']
        overall = round(SRate, 2) if SRate != '?' else '?'
        if overall == '?' or overall < float(cfg.get(MODE, 'overall_down_th')):
            tframe.overall_colour = cfg.get(MODE, 'down_colour')
        elif overall < float(cfg.get(MODE, 'overall_unstable_th')):
            tframe.overall_colour = cfg.get(MODE, 'unstable_colour')
        else:
            tframe.overall_colour = cfg.get(MODE, 'up_colour')
        tframe.success_rate = str(overall)
        tframe.job_success_rates = {}
        tframe.job_success_rate_col = {}
        for jobname, yaml_file in bug_ranking_files.items():
            OvAll = oil_stats['jobs'][jobname]['success rate']
            success = round(OvAll, 2) if OvAll != '?' else '?'
            if success == '?' or success < float(js_down_th[jobname]):
                tframe.job_success_rate_col[jobname] = cfg.get(MODE, 'down_colour')
            elif success < float(js_unstable_th[jobname]):
                tframe.job_success_rate_col[jobname] = \
                    cfg.get(MODE, 'unstable_colour')
            else:
                tframe.job_success_rate_col[jobname] = cfg.get(MODE, 'up_colour')
            tframe.job_success_rates[jobname] = str(success)

        return tframe


    def load_from_yaml_file(self, file_location):
        """Return data from yaml file."""

        if not os.path.exists(file_location):
            raise AbsentYamlError("{} missing".format(file_location))

        with open(file_location, 'r') as oil_file:
            return yaml.load(oil_file)
