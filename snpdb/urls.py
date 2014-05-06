__author__ = 'mcobb'

from django.conf.urls import *

urlpatterns = patterns('',
                       # Sends requests to filter functions
                       # url(r'^search/snp', 'snpdb.views.snptype_filter'),
                       url(r'^snptype/search', 'snpdb.views.snptype_filter'),
                       url(r'^snp/search', 'snpdb.views.snp_filter'),
                       url(r'^statistics/search', 'snpdb.views.statistics_filter'),
                       url(r'^effect/search', 'snpdb.views.effect_filter'),
                       url(r'^filter/search', 'snpdb.views.filter_filter'),
                       url(r'^gene-snps/search', 'snpdb.views.gene_snps_filter'),
                       url(r'^library-snps/search', 'snpdb.views.library_snps_filter'),
                       url(r'^library-summary/search', 'snpdb.views.library_summary'),


                       #Search Functions
                       url(r'^library-summary', 'snpdb.views.library_summary'),
                       url(r'^gene-snps', 'snpdb.views.gene_snps'),
                       url(r'^library-snps', 'snpdb.views.library_snps'),

                       # Basic Table Views:
                       url(r'^snptype', 'snpdb.views.snp_type'),
                       url(r'^snp','snpdb.views.snp'),
                       url(r'^statistics', 'snpdb.views.statistics'),
                       url(r'^effect', 'snpdb.views.effect'),
                       url(r'^filter', 'snpdb.views.filter'),
                       url(r'^$', 'snpdb.views.dashboard'),
                       )