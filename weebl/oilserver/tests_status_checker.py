#! /usr/bin/env python3
import os
import shutil
import utils
from datetime import datetime
from oilserver import views
from django.http import HttpRequest
from common_test_methods import WeeblTestCase
from collections import namedtuple
from oilserver.status_checker import StatusChecker
from oilserver import models


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
        up_service_status = models.ServiceStatus()
        st8_sit = self.status_checker.determine_current_oil_state_and_situation
        state_and_situation = st8_sit(environment, models.ServiceStatus)
        self.assertEqual(state_and_situation[0], 'up')
        self.assertEqual(state_and_situation[1], [])

    def test_calc_time_since_last_checkin(self):
        timestamp_now = utils.time_now()
        timestamp_old = datetime.strptime("Jan 1 2000 00:00:00",
                                          "%b %d %Y %H:%M:%S")
        (delta_now, time_msg_now) =\
            self.status_checker.calc_time_since_last_checkin(timestamp_now)
        (delta_old, time_msg_old) =\
            self.status_checker.calc_time_since_last_checkin(timestamp_old)
        self.assertEqual(delta_now, 0)
        nums_in_msg = [int(s) for s in time_msg_old.split() if s.isdigit()]
        num = nums_in_msg[0]
        approx = round(delta_old/60/60/24/7)
        difference = abs(approx - num)
        self.assertTrue(difference < 5)
        self.assertTrue("Jenkins has not checked in for" in time_msg_old)

    def test_get_overdue_state(self):
        unstable_th = self.settings.check_in_unstable_threshold
        down_th = self.settings.check_in_down_threshold

        up = self.status_checker.get_overdue_state(0)
        unstable = self.status_checker.get_overdue_state(unstable_th+1)
        down = self.status_checker.get_overdue_state(down_th+1)
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
