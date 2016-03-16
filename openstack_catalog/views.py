from django.shortcuts import render


def index(request):
    return render(request, 'index.html', {})


def create_asset(request):
    return render(request, 'create_asset.html', {})
