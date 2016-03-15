from django.conf import settings
from django.shortcuts import render


def index(request):
    return render(request, 'index.html',
                  {'GLARE_API_ENRYPOINT': settings.GLARE_API_ENTRYPOINT})
