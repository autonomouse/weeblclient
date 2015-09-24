#! /usr/bin/env python3
from oilserver import views
from django.http import HttpRequest
from common_test_methods import WeeblTestCase


class DevSmokeTests(WeeblTestCase):
    def test_main_page(self):
        request = HttpRequest()
        page_title = b'Weebl - Main Page'
        response = views.main_page(request)
        self.assertIn(page_title, response.content)
        self.assertIn(b'<!-- Oil Stats -->', response.content)
        self.assertIn(b'Filters', response.content)
        self.assertIn(b'Breakdown by category', response.content)

    def test_settings_page(self):
        request = HttpRequest()
        page_title = b'Weebl - Settings'
        response = views.settings_page(request)
        self.assertIn(page_title, response.content)
        self.assertIn(b'<!-- Oil Stats -->', response.content)
        self.assertIn(b'Settings', response.content)
