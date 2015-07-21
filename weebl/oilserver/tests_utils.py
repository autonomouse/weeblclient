#! /usr/bin/env python3
import utils
import random
from common_test_methods import WeeblTestCase
from datetime import datetime, timedelta
from django.core.validators import URLValidator, ValidationError
from time import sleep


class UtilsTests(WeeblTestCase):

    def test_time_now(self):
        timestamp_now = utils.time_now()
        ts_type = type(timestamp_now)
        self.assertTrue(ts_type is datetime)

    def test_generate_uuid(self):
        uuid = utils.generate_uuid()
        self.assertTrue(utils.uuid_check(uuid))

    def test_get_weebl_version(self):
        version = utils.get_weebl_version()
        v_type = type(version)
        self.assertTrue(v_type is str)

    def test_generate_random_string(self):
        num = random.randint(5, 9)
        string1 = utils.generate_random_string(num, uppercase=False)
        string2 = utils.generate_random_string(num, uppercase=True)
        randomstr_type = type(string1)
        self.assertTrue(randomstr_type is str)
        self.assertEqual(len(string1), num)
        self.assertFalse(string1[0].isupper())
        self.assertTrue(string2[0].isupper())

    def test_generate_random_url(self):
        num = random.randint(5, 9)
        val = URLValidator()
        url = utils.generate_random_url(num)
        (protocol_and_subdomain, second_lvl_dom, top_lvl_dom) = url.split('.')
        try:
            val(url)
            valid_url = True
        except ValidationError:
            valid_url = False
        self.assertTrue(valid_url)
        self.assertEqual(len(second_lvl_dom), num)

    def test_time_since(self):
        timestamp = datetime.strptime("Jan 1 2000 00:00:00",
                                      "%b %d %Y %H:%M:%S")
        delta = utils.time_since(timestamp)
        ts_type = type(delta)
        self.assertTrue(ts_type is timedelta)

    def test_time_difference_less_than_x_mins(self):
        timestamp = datetime.strptime("Jan 1 2000 00:00:00",
                                      "%b %d %Y %H:%M:%S")
        no_time = 0
        sleep(2)
        wrong_short_0 = utils.time_difference_less_than_x_mins(
            utils.time_now(), no_time)
        wrong_long_0 = utils.time_difference_less_than_x_mins(
            timestamp, no_time)

        no_time = 10
        right_short_10 = utils.time_difference_less_than_x_mins(
            utils.time_now(), no_time)
        wrong_long_10 = utils.time_difference_less_than_x_mins(
            timestamp, no_time)

        self.assertFalse(wrong_short_0)
        self.assertFalse(wrong_long_0)
        self.assertTrue(right_short_10)
        self.assertFalse(wrong_long_10)

    def test_uuid_check(self):
        good_uuid = "12345678-abcd-ABCD-1234-123abc123abc"
        bad_uuid = "turnips"
        self.assertTrue(utils.uuid_check(good_uuid))
        self.assertFalse(utils.uuid_check(bad_uuid))
