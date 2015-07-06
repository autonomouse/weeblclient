import os
import json
import yaml
import utils
import pytz
from django.contrib.sites.models import Site
from __init__ import __version__
from collections import namedtuple


class StatusChecker():
    """ """

    def __init__(self, weebl_setting, environment):
        self.current_site = self.get_current_site
        if repr(weebl_setting.objects.all()) == '[]':
            raise Exception("No current site - fixtures must be loaded first!")
        self.weebl_setting = weebl_setting.objects.get(pk=self.current_site)
        self.environment = environment


    def get_current_site(self):
        return Site.objects.get_current().id


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

        env.oil_situation = []
        status = environment.current_situation

        delta, time_msg = self.calc_time_since_last_checkin(environment.last_active)

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
