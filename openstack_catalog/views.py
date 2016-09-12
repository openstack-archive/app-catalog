from django.shortcuts import render
from django.conf import settings


def index(request):
    return render(request, 'index.html', {'GLARE_URL': settings.GLARE_URL})
