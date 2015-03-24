
from django.shortcuts import render

def main_page(request):
    data = {'title': 'main_page'}
    return render(request, 'main_page.html', data)

def oil_stats(request):
    data = {'title': 'oil_stats'}
    return render(request, 'oil_stats.html', data)

def job_specific_bugs_list(request, job):
    data = {'title': 'job_specific_bugs_list',
            'job': job,}
    return render(request, 'job_specific_bugs_list.html', data)

def specific_bug_info(request, bug_id):
    data = {'title': 'specific_bug_info',
            'bug_id': bug_id,}
    return render(request, 'specific_bug_info.html', data)

def bug_specific_pipelines(request, bug_id):
    data = {'title': 'bug_specific_pipelines',
            'bug_id': bug_id,}
    return render(request, 'bug_specific_pipelines.html', data)

def pipeline_specific_bugs(request, pipeline_id):
    data = {'title': 'pipeline_specific_bugs',
            'pipeline_id': pipeline_id,}
    return render(request, 'pipeline_specific_bugs.html', data)

def maintenance_history(request):
    data = {'title': 'maintenance_history'}
    return render(request, 'maintenance_history.html', data)

def event_specific_details(request, event_id):
    data = {'title': 'event_specific_details',
            'event_id': event_id,}
    return render(request, 'event_specific_details.html', data)

def tools(request):
    data = {'title': 'tools'}
    return render(request, 'tools.html', data)

def specific_vendor_info(request, vendor):
    data = {'title': 'specific_vendor_info',
            'vendor': vendor,}
    return render(request, 'specific_vendor_info.html', data)

def charts(request):
    data = {'title': 'charts'}
    return render(request, 'charts.html', data)

def categories_and_tags(request):
    data = {'title': 'categories_and_tags'}
    return render(request, 'categories_and_tags.html', data)

def bugs_list(request):
    data = {'title': 'bugs_list'}
    return render(request, 'bugs_list.html', data)

def vendor_and_hardware(request):
    data = {'title': 'vendor_and_hardware'}
    return render(request, 'vendor_and_hardware.html', data)

def oil_control(request):
    data = {'title': 'oil_control'}
    return render(request, 'oil_control.html', data)

def specific_machine_history(request, machine):
    data = {'title': 'specific_machine_history',
            'machine': machine,}
    return render(request, 'specific_machine_history.html', data)

