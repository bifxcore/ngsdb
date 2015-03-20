__author__ = 'mcobb'

from django.conf.urls import *
from django.views.generic import RedirectView

urlpatterns = patterns('',
                      # Sends requests to filter functions
                      url(r'^chromosome-library-snps-summary/search', 'snpdb.views.chromosome_library_snp_summary_filter'),
                      url(r'^compare-gene-lib-filter/search', 'snpdb.views.compare_gene_lib_filter_results_effect'),
                      url(r'^compare-gene-lib/search', 'snpdb.views.compare_gene_lib_filter'),
                      url(r'^effect/search', 'snpdb.views.effect_filter'),
                      url(r'^filter/search', 'snpdb.views.filter_filter'),
                      url(r'^gene-snps/search', 'snpdb.views.gene_snps_filter'),
                      url(r'^compare-libs/search', 'snpdb.compare_libraries_view.compare_isec_search'),
                      url(r'^chrom-region/search', 'snpdb.views.chrom_region_search'),
                      url(r'^chrom-region-filter', 'snpdb.views.chrom_region_filter'),

                      url(r'^impact-snps/search', 'snpdb.compare_libraries_view.impact_snps'),
                      url(r'^library-chromosome-snps/search', 'snpdb.views.library_chromosome_snps_filter'),
                      url(r'^library-gene-snps/search', 'snpdb.views.library_gene_snps_filter'),
                      url(r'^snp/search', 'snpdb.views.snp_filter_result'),
                      url(r'^snptype/search', 'snpdb.views.snptype_filter'),
                      url(r'^statistics/search', 'snpdb.views.statistics_filter'),
					  url(r'^gene-snp-summary', 'snpdb.views.gene_snp_summary'),

                      #Search Functions
                      url(r'^chromosome-library-snp-summary', 'snpdb.views.chromosome_library_snp_summary'),
                      url(r'^compare-gene-lib', 'snpdb.views.compare_gene_lib'),
                      url(r'^gene-list', 'snpdb.views.gene_list'),
                      url(r'^library-chromosome-snps', 'snpdb.views.library_chromosome_snps'),
                      url(r'^library-gene-snps', 'snpdb.views.library_gene_snps'),
                      url(r'^library-snp-summary', 'snpdb.views.library_snp_summary'),
                      url(r'^compare-libs', 'snpdb.compare_libraries_view.compare_libs'),
                      url(r'^gene-feature', 'snpdb.views.gene_feature'),
                      url(r'^chrom-region', 'snpdb.views.chrom_region'),
                      url(r'^snpdb-flowchart', 'snpdb.views.snpdb_flowchart'),


                      # Basic Table Views: Currently not accessible to users as the information is not relevant to researchers.
                      url(r'^effect', 'snpdb.views.effect'),
                      url(r'^filter', 'snpdb.views.snp_filter'),
                      url(r'^snptype', 'snpdb.views.snp_type'),
                      url(r'^snp','snpdb.views.snp_view'),
                      url(r'^statistics', 'snpdb.views.statistics'),
                      url(r'^contigs', 'snpdb.views.get_chromosome_size'),
                      url(r'^$', 'snpdb.views.dashboard'),
                      )