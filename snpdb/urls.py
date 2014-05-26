__author__ = 'mcobb'

from django.conf.urls import *

urlpatterns = patterns('',
                       # Sends requests to filter functions
                       # url(r'^search/snp', 'snpdb.views.snptype_filter'),
                       url(r'^compare-gene-lib-filter/search', 'snpdb.views.compare_gene_lib_filter_results'),
                       url(r'^compare-gene-lib/search', 'snpdb.views.compare_gene_lib_filter'),
                       url(r'^snptype/search', 'snpdb.views.snptype_filter'),
                       url(r'^snp/search', 'snpdb.views.snp_filter_result'),
                       url(r'^statistics/search', 'snpdb.views.statistics_filter'),
                       url(r'^effect/search', 'snpdb.views.effect_filter'),
                       url(r'^filter/search', 'snpdb.views.filter_filter'),
                       url(r'^gene-snps/search', 'snpdb.views.gene_snps_filter'),
                       url(r'^library-gene-snps/search', 'snpdb.views.library_gene_snps_filter'),
                       url(r'^library-snp-summary/search', 'snpdb.views.library_snps'),
                       url(r'^library-chromosome-snps/search', 'snpdb.views.library_chromosome_snps_filter'),
                       url(r'^chromosome-library-snps-summary/search', 'snpdb.views.chromosome_library_snp_summary_filter'),


                       #Search Functions
                       url(r'^library-snp-summary', 'snpdb.views.library_snp_summary'),
                       url(r'^chromosome-library-snp-summary', 'snpdb.views.chromosome_library_snp_summary'),
                       url(r'^gene-snps', 'snpdb.views.gene_snps'),
                       url(r'^library-gene-snps', 'snpdb.views.library_gene_snps'),
                       url(r'^library-chromosome-snps', 'snpdb.views.library_chromosome_snps'),
                       url(r'^compare-gene-lib', 'snpdb.views.compare_gene_lib'),


                       # Basic Table Views:
                       url(r'^snptype', 'snpdb.views.snp_type'),
                       url(r'^snp','snpdb.views.snp'),
                       url(r'^statistics', 'snpdb.views.statistics'),
                       url(r'^effect', 'snpdb.views.effect'),
                       url(r'^filter', 'snpdb.views.snp_filter'),
                       url(r'^$', 'snpdb.views.dashboard'),
                       )