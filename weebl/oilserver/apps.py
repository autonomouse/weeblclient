from django.apps import AppConfig
from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key


class OilserverConfig(AppConfig):

    name = 'oilserver'
    models.signals.post_save.connect(create_api_key, sender=User)
