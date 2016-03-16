from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from openstack_catalog import views

urlpatterns = [url(r'^$', views.index),
               url(r'^create_asset$', views.create_asset)]

urlpatterns += staticfiles_urlpatterns()
