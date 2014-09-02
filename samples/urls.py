from django.conf.urls import *

urlpatterns = patterns('',


    url(r'^authors/$','samples.views.author'),
    url(r'^librarylist/$', 'samples.views.librarylist'),
    url(r'^listlibraries/(?P<libtype>.+)/(?P<analysis_status>.+)/','samples.views.ListLibraries'),


    )