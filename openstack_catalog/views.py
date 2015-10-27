from django.shortcuts import render


def index(request):
    return render(request, 'index.html', {})

def testicons(request):
    return render(request, 'testicons.html', {})
