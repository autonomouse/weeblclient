from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import redirect


def main_page(request):
    return render(request, 'index.html')


def logout_view(request):
    logout(request)
    return redirect('/')
