import os
import tempfile
import yaml
import shutil
from random import random, randint
from django.test import TestCase
from datetime import datetime
from dateutil.parser import parse


class WeeblTestCase(TestCase):
    fixtures = ['initial_settings.yaml']
