#! /usr/bin/env python3
import utils
from common_test_methods import WeeblTestCase
from oilserver.status_checker import StatusChecker
from oilserver import models
from freezegun import freeze_time


class StatusCheckerTests(WeeblTestCase):

    def setUp(self):
        self.settings = models.WeeblSetting()
        self.status_checker = StatusChecker(self.settings)

    def test_get_current_oil_state(self):
        self.test_determine_current_oil_state_and_situation()

    def test_get_current_oil_situation(self):
        self.test_determine_current_oil_state_and_situation()

    def test_determine_current_oil_state_and_situation(self):
        environment = models.Environment()
        jenkins = models.Jenkins()
        jenkins.environment = environment
        st8_sit = self.status_checker.determine_current_oil_state_and_situation
        state_and_situation = st8_sit(environment, models.ServiceStatus)
        self.assertEqual(state_and_situation[0], 'up')
        self.assertEqual(state_and_situation[1], [])

    def test_calc_time_since_last_checkin(self):
        with freeze_time("Jan 1 2000 00:00:00"):
            timestamp_earlier = utils.time_now()
        with freeze_time("Jan 1 2000 12:00:00"):
            timestamp_later = utils.time_now()
            test_method = self.status_checker.calc_time_since_last_checkin
            (delta_earlier, time_msg_earlier) = test_method(timestamp_earlier)
            (delta_later, time_msg_later) = test_method(timestamp_later)
        nums_in_msg = [int(s) for s in time_msg_earlier.split() if s.isdigit()]
        num = nums_in_msg[0]
        self.assertEqual(delta_later, 0)
        self.assertEqual(num, 12)
        self.assertEqual(delta_earlier / 60 / 60, 12.0)
        self.assertTrue("Jenkins has not checked in for" in time_msg_earlier)

    def test_get_overdue_state(self):
        unstable_th = self.settings.check_in_unstable_threshold
        down_th = self.settings.check_in_down_threshold

        up = self.status_checker.get_overdue_state(0)
        unstable = self.status_checker.get_overdue_state(unstable_th + 1)
        down = self.status_checker.get_overdue_state(down_th + 1)
        self.assertEqual(up, 'up')
        self.assertEqual(unstable, 'unstable')
        self.assertEqual(down, 'down')

    def test_set_oil_state(self):
        initial_oil_state = 'up'
        initial_oil_situation = []
        new_state = 'down'
        msg = "test msg"

        (oil_state, oil_situation) = self.status_checker.set_oil_state(
            initial_oil_state, initial_oil_situation, new_state, msg)

        self.assertNotEqual(initial_oil_state, oil_state)
        self.assertIn(msg, oil_situation)
        self.assertIn(new_state, oil_state)
