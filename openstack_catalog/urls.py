from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = patterns('',
     url(r'^$', views.index),
)

urlpatterns += staticfiles_urlpatterns()
