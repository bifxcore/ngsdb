__author__ = 'mcobb'

from django.conf.urls import *

urlpatterns = patterns('',
                       # Sends requests to filter functions
                       url(r'^snp/search', 'snpdb.views.snp_filter'),
                       # url(r'^search/statistics', 'snpdb.views.statistics_filter'),
                       # url(r'^search/snptype', 'snpdb.views.snptype_filter'),
                       # url(r'^search/effect', 'snpdb.views.effect_filter'),
                       # url(r'^search/filter', 'snpdb.views.filter_filter'),

                       url(r'^snp/$','snpdb.views.snp'),
                       url(r'^statistics/', 'snpdb.views.statistics'),
                       url(r'^snptype/', 'snpdb.views.snp_type'),
                       url(r'^effect/', 'snpdb.views.effect'),
                       url(r'^filter/', 'snpdb.views.filter'),
                       url(r'^$', 'snpdb.views.dashboard'),
                       )