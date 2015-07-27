import utils


class StatusChecker():
    """ """

    def __init__(self, settings):
        self.settings = settings

    def get_current_oil_state(self, jenkins, ServiceStatus):
        state_and_situation = self.determine_current_oil_state_and_situation(
            jenkins, ServiceStatus)
        return state_and_situation[0]

    def get_current_oil_situation(self, jenkins, ServiceStatus):
        state_and_situation = self.determine_current_oil_state_and_situation(
            jenkins, ServiceStatus)
        return state_and_situation[1]

    def determine_current_oil_state_and_situation(self, environment, ServStat):
        oil_state = 'up'
        oil_situation = []

        #initial_status = environment.jenkins.service_status.name
        last_active = environment.jenkins.service_status_updated_at
        delta, time_msg = self.calc_time_since_last_checkin(last_active)

        overdue_state = self.get_overdue_state(delta)
        if overdue_state is not None:
            oil_state, oil_situation = self.set_oil_state(
                oil_state, oil_situation, overdue_state, time_msg)

        environment.service_status = ServStat.objects.get(name=oil_state)
        return (oil_state, oil_situation)

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

        msg = "Jenkins has not checked in for {} {}"
        if weeks > 0:
            timestr = 'weeks' if weeks > 1 else 'week'
            time_msg = msg.format(weeks, timestr)
        elif days > 0:
            timestr = 'days' if days > 1 else 'day'
            time_msg = msg.format(days, timestr)
        elif hours > 0:
            timestr = 'hours' if hours > 1 else 'hour'
            time_msg = msg.format(hours, timestr)
        elif minutes > 0:
            timestr = 'minutes' if minutes > 1 else 'minute'
            time_msg = msg.format(minutes, timestr)
        else:
            time_msg = ''
        return (delta, time_msg)

    def get_overdue_state(self, delta):
        unstable_th = self.settings.check_in_unstable_threshold
        down_th = self.settings.check_in_down_threshold

        errstate = 'up'
        if delta is None or delta > float(down_th):
            errstate = 'down'
        elif delta > float(unstable_th):
            errstate = 'unstable'
        return errstate

    def set_oil_state(self, oil_state, oil_situation, new_state, msg):
        # Set state:
        if oil_state != 'down':
            oil_state = new_state

        # Set message:
        if oil_state != 'up' and msg != '':
            oil_situation.append(msg)
        return (oil_state, oil_situation)
