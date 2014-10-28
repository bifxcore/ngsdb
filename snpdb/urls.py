__author__ = 'mcobb'

from django.conf.urls import *
from django.views.generic import RedirectView

urlpatterns = patterns('',
                      # Sends requests to filter functions
                      url(r'^chromosome-library-snps-summary/search', 'snpdb.views.chromosome_library_snp_summary_filter'),
                      url(r'^compare-gene-lib-filter/search', 'snpdb.views.compare_gene_lib_filter_results_effect'),
                      url(r'^compare-gene-lib/search', 'snpdb.views.compare_gene_lib_filter'),
                      url(r'^compare-two-libs/search', 'snpdb.views.difference_two_libraries'),
                      url(r'^effect/search', 'snpdb.views.effect_filter'),
                      url(r'^filter/search', 'snpdb.views.filter_filter'),
                      url(r'^gene-snps/search', 'snpdb.views.gene_snps_filter'),
                      url(r'^test', 'snpdb.views.effects_by_vcf'),

                      url(r'^impact2/search', 'snpdb.views.impact_snps2'),
                      url(r'^impact-snps/search', 'snpdb.views.impact_snps'),
                      url(r'^library-chromosome-snps/search', 'snpdb.views.library_chromosome_snps_filter'),
                      url(r'^library-gene-snps/search', 'snpdb.views.library_gene_snps_filter'),
                      # url(r'^library-snp-summary/filter/search', 'snpdb.views.library_snps_filter'),
                      url(r'^library-snp-summary/search', 'snpdb.views.library_snps'),
                      # url(r'^multi-gene-snps/search', 'snpdb.views.multi_gene_snps_filter'),
                      # url(r'^multi-gene-library-snps/search', 'snpdb.views.multi_gene_library_snps_filter'),
                      url(r'^snp/search', 'snpdb.views.snp_filter_result'),
                      url(r'^snptype/search', 'snpdb.views.snptype_filter'),
                      url(r'^statistics/search', 'snpdb.views.statistics_filter'),
                      # url(r'^difference-two-libraries/search', 'snpdb.views.difference_two_libraries_filter'),

                      #Search Functions
                      url(r'^chromosome-library-snp-summary', 'snpdb.views.chromosome_library_snp_summary'),
                      url(r'^compare-gene-lib', 'snpdb.views.compare_gene_lib'),
                      url(r'^gene-list', 'snpdb.views.gene_list'),
                      url(r'^gene-snps', 'snpdb.views.gene_snps'),
                      # url(r'^multi-gene-snps', 'snpdb.views.multi_gene_snps'),
                      # url(r'^multi-gene-library-snps', 'snpdb.views.multi_gene_library_snps'),
                      url(r'^library-chromosome-snps', 'snpdb.views.library_chromosome_snps'),
                      url(r'^library-gene-snps', 'snpdb.views.library_gene_snps'),
                      url(r'^library-snp-summary', 'snpdb.views.library_snp_summary'),
                      url(r'^diff-libraries2', 'snpdb.views.diff_libraries2'),
                      url(r'^difference-two-libraries', 'snpdb.views.difference_two_libraries'),
                      url(r'^compare-libs', 'snpdb.views.compare_two_libraries'),
                      url(r'^gene-feature', 'snpdb.views.gene_feature'),
                      url(r'^chrom-region', 'snpdb.views.chrom_region'),


                      # Basic Table Views:
                      url(r'^effect', 'snpdb.views.effect'),
                      url(r'^filter', 'snpdb.views.snp_filter'),
                      url(r'^snptype', 'snpdb.views.snp_type'),
                      url(r'^snp','snpdb.views.snp'),
                      url(r'^statistics', 'snpdb.views.statistics'),
                      url(r'^contigs', 'snpdb.views.get_chromosome_size'),
                      url(r'^$', 'snpdb.views.dashboard'),
                      )