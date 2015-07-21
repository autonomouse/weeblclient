#! /usr/bin/env python3
from common_test_methods import WeeblTestCase
from oilserver.forms import SettingsForm

class SettingsFormTests(WeeblTestCase):
    def test_settings_form(self):
        form_data = {'check_in_unstable_threshold': '99999',
                     'check_in_down_threshold': '999999',
                     'low_build_queue_threshold': '99999',
                     'overall_unstable_th': '99999',
                     'overall_down_th': '999999',
                     'down_colour': 'pinkest',
                     'unstable_colour': 'pinker',
                     'up_colour': 'pink',
                     'weebl_documentation': 'https://mock.url.com',}
        form = SettingsForm(data=form_data)
        self.assertEqual(form.is_valid(), True)


