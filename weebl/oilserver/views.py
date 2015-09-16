from django.contrib.sites.models import Site
from django.shortcuts import render
from oilserver import models
from oilserver.forms import SettingsForm


current_site = Site.objects.get_current().id
settings = models.WeeblSetting.objects.get(pk=current_site)


def generate_generic_data_dict(title, environments, time_range=None):
    data = {}
    data['title'] = title
    if time_range:
        data['time_range'] = time_range
    data['settings'] = settings
    data['env'] = {}
    data['build_executors'] = {}
    data['jenkins'] = {}
    for environment in environments:
        data['env'][environment.name] = environment
    return data


def main_page(request):
    return render(request, 'index.html')


def weekly_main_page(request, time_range='weekly'):
    return main_page(request, time_range)


def job_specific_bugs_list(request, job, time_range='daily',
                           specific_env='all'):
    if specific_env == 'all':
        environments = models.Environment.objects.all()
    else:
        environments = [models.Environment.objects.get(name=specific_env)]
    data = generate_generic_data_dict('Job Specific Bugs List',
                                      environments, time_range)
    data['job'] = job
    return render(request, 'page_job_specific_bugs_list.html', data)


def settings_page(request):
    data = {'updated': None}
    original = models.WeeblSetting.objects.get(pk=current_site)

    if request.method != 'POST':
        # Before send the form:
        form = SettingsForm(instance=original)
    else:
        # Upon receipt of the form:
        req_data = request.POST.copy()
        req_data[''] = original.site_id
        form = SettingsForm(req_data, instance=settings)
        if form.is_valid():
            form.save()
            data['updated'] = True
        else:
            data['updated'] = False
    data['form'] = form
    return render(request, 'page_settings.html', data)


def environment_page(request, uuid):
    env = models.Environment.objects.get(uuid=uuid)
    data = generate_generic_data_dict('Weebl - Environment', [env])
    data['title'] = 'Weebl - Environment: {}'.format(env.name)
    if hasattr(env, 'jenkins'):
        data['build_executors'] = env.jenkins.buildexecutor_set.values()
        data['jenkins'] = env.jenkins
    return render(request, 'page_environment.html', data)
