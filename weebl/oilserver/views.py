from django.contrib.sites.models import Site
from django.shortcuts import render
from oilserver import models
from oilserver.forms import SettingsForm

def main_page(request):
    return render(request, 'index.html')
