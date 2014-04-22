__author__ = 'mcobb'

from django.conf.urls import *

urlpatterns = patterns('',


    url(r'^snp/$','snpdb.views.snp'),
    url(r'^statistics/', 'snpdb.views.statistics'),


    )