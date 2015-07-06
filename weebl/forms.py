from django.forms import ModelForm
from oilserver.models import WeeblSetting


class SettingsForm(ModelForm):
    class Meta:
        model = WeeblSetting
        exclude = ['site']
