__author__ = 'mcobb'

from django.conf.urls import *

urlpatterns = patterns('',
                       # Sends requests to filter functions
                       url(r'^compare-gene-lib-filter/search', 'snpdb.views.compare_gene_lib_results'),
                       url(r'^gene-snps/search', 'snpdb.views.gene_snps_filter'),
                       url(r'^compare-libs/search', 'snpdb.compare_libraries_view.compare_isec_search'),
                       url(r'^chrom-region-filter', 'snpdb.views.chrom_region_filter'),
                       url(r'^chrom-region/search', 'snpdb.views.chrom_region_search'),
                       url(r'^chromosome-library-snp-summary/filter', 'snpdb.views.chromosome_library_snp_summary_filter'),
                       url(r'^impact-snps/search', 'snpdb.compare_libraries_view.impact_snps'),
                       url(r'^library-gene-snps/search', 'snpdb.views.library_gene_snps_filter'),
                       url(r'^gene-snp-summary', 'snpdb.compare_libraries_view.gene_snp_summary'),

                       #Search Functions
                       url(r'^chromosome-library-snp-summary', 'snpdb.views.chromosome_library_snp_summary'),
                       url(r'^compare-gene-lib', 'snpdb.views.compare_gene_lib'),
                       url(r'^gene-list', 'snpdb.views.gene_list'),
                       url(r'^library-gene-snps', 'snpdb.views.library_gene_snps'),
                       url(r'^library-snp-summary', 'snpdb.views.library_snp_summary'),
                       url(r'^compare-libs', 'snpdb.compare_libraries_view.compare_libs'),
                       url(r'^gene-feature', 'snpdb.views.gene_feature'),
                       url(r'^chrom-region', 'snpdb.views.chrom_region'),
                       url(r'^snpdb-flowchart', 'snpdb.views.snpdb_flowchart'),


                       #CNV Views
                       url(r'^compare-cnv-libraries', 'snpdb.cnv_views.compare_cnv_libraries'),
                       # url(r'^compare-cnv-libraries', 'snpdb.cnv_views.compare_libraries_cnv_graphs'),


                       # Basic Table Views: Currently not accessible to users as the information is not relevant to researchers.
                       url(r'^$', 'snpdb.views.dashboard'),

                       # Gowthaman's views
                       url(r'^comparelibs/somy/(?P<experimentId>.+)/', 'snpdb.compare_libraries_view.compare_libraries_somy'),
                       url(r'^comparelibs/cnv/(?P<experimentId>.+)/', 'snpdb.compare_libraries_view.compare_libraries_cnv'),
                       url(r'^comparelibs/cnvfilter/(?P<experimentId>.+)/', 'snpdb.compare_libraries_view.compare_libs_cnv'),
                       url(r'^create-graphs', 'snpdb.compare_libraries_view.create_cnv_graphs'),


                       # url(r'^create-graphs-cnv', 'snpdb.compare_libraries_view.compare_libraries_cnv_graphs'),

                       )