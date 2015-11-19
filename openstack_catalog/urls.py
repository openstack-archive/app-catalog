from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from openstack_catalog import views

urlpatterns = patterns('', url(r'^$', views.index))

urlpatterns += staticfiles_urlpatterns()
