
from django.shortcuts import render

def main_page(request):
    data = {'title': 'main_page'}
    return render(request, 'main_page.html', data)

def job_specific_bugs_list(request, job):
    data = {'title': 'job_specific_bugs_list',
            'job': job,}
    return render(request, 'job_specific_bugs_list.html', data)

