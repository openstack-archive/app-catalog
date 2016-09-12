from django.conf import settings
from django.shortcuts import render


def index(request):
    return render(request, 'index.html',
                  {'GLARE_URL': settings.GLARE_URL,
                   'LAUNCHPAD_ADMIN_GROUPS': settings.LAUNCHPAD_ADMIN_GROUPS})
