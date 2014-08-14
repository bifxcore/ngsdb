from snpdb.models import *
from django.shortcuts import render_to_response, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from utils import build_orderby_urls
from django.db.models import *
from django_boolean_sum import BooleanSum
from templatetags.snp_filters import *
from django.template import RequestContext
from GChartWrapper import *
from collections import *
import subprocess
import datetime
import os
import csv

low_effects = ["SYNONYMOUS_START", "NON_SYNONYMOUS_START", "START_GAINED", "SYNONYMOUS_CODING", "SYNONYMOUS_STOP"]
high_effects = ["SPLICE_SITE_ACCEPTOR", "SPLICE_SITE_DONOR", "START_LOST", "EXON_DELETED", "FRAME_SHIFT", "STOP_GAINED", "STOP_LOST", "RARE_AMINO_ACI"]
moderate_effects = ["NON_SYNONYMOUS_CODING", "CODON_CHANGE", "CODON_INSERTION", "CODON_CHANGE_PLUS_CODON_INSERTION",
                    "CODON_DELETION", "CODON_CHANGE_PLUS_CODON_DELETION", "UTR_5_DELETED", "UTR_3_DELETED"]
modifier_effects = ["UTR_5_PRIME", "UTR_3_PRIME", "REGULATION", "UPSTREAM", "DOWNSTREAM", "GENE", "TRANSCRIPT", "EXON",
                    "INTRON_CONSERVED", "INTRON", "INTRAGENIC", "INTERGENIC", "INTERGENIC_CONSERVED", "NONE", "CHROMOSOME", "CUSTOM", "CDS"]


#todo set up a cron job to auto-create the pie charts and counts weekly/monthly and store them for quicker access.
def dashboard(request):
	title = "SNP Dashboard"

	lib_count = SNP.objects.values("library__librarycode").distinct().annotate(Count('snp_id'))
	lib_snps = []
	lib_snp_total = 0
	for each in lib_count.iterator():
		lib_snps.append(each['snp_id__count'])
		lib_snp_total += each['snp_id__count']
	print "lib_count"

	org_count = SNP.objects.values("library__organism__organismcode").distinct().annotate(Count('snp_id'))
	org_snps = []
	org_snp_total = 0
	for each in org_count.iterator():
		org_snps.append(each['snp_id__count'])
		org_snp_total += each['snp_id__count']
	print "org_count"

	path = '/Users/mcobb/Documents/djangoProjects/ngsdb03/snpdb/gcharts/%s_impact.csv'
	image_path = 'snpdb/snps_by_%s.png'

	#read count files
	high_count = read(path % 'high')
	low_count = read(path % 'low')
	moderate_count = read(path % 'moderate')
	modifier_count = read(path % 'modifier')
	impact_count = read(path % 'impact')

	images = [image_path % 'library', image_path % 'organism', image_path % 'impact', image_path % 'high_impact',
	          image_path % 'low_impact', image_path % 'moderate_impact', image_path % 'modifier_impact']
	print images
	totals = [lib_snp_total, org_snp_total]
	return render_to_response('snpdb/dashboard.html', {"title": title,
	                                                   "images": images,
	                                                   "totals": totals,
	                                                   "lib_count": lib_count,
	                                                   "org_count": org_count,
	                                                   "impact_count": impact_count,
	                                                   "high_count": high_count,
	                                                   "low_count": low_count,
	                                                   "moderate_count": moderate_count,
	                                                   "modifier_count": modifier_count,
	                                                   },  context_instance=RequestContext(request))


# Returns the general effect table view.
def effect(request):
	order_by = request.GET.get('order_by', 'effect')
	current_url = request.get_full_path()
	snp_effect_list = Effect.objects.all().order_by(order_by)
	paginator = Paginator(snp_effect_list, 50)
	page = request.GET.get('page')

	# Calls utils method to append new filters or order_by to the current url
	filter_urls = build_orderby_urls(request.get_full_path(), ['snp_id', 'effect', 'effect_class',
	                                                           'effect_string', 'effect_group'])
	try:
		snp_effect = paginator.page(page)
	except PageNotAnInteger:
		snp_effect = paginator.page(1)
	except EmptyPage:
		snp_effect = paginator.page(paginator.num_pages)

	toolbar_max = min(snp_effect.number + 4, paginator.num_pages)
	toolbar_min = max(snp_effect.number - 4, 0)

	return render_to_response('snpdb/effect.html', {"snp_effect": snp_effect,
	                                                "filter_urls": filter_urls,
	                                                "paginator": paginator,
	                                                "toolbar_max": toolbar_max,
	                                                "toolbar_min": toolbar_min,
	                                                "current_url": current_url},
	                          context_instance=RequestContext(request))


# Returns the general filter table view
def snp_filter(request):
	order_by = request.GET.get('order_by', 'snp')
	filter_list = Filter.objects.all().order_by(order_by)
	paginator = Paginator(filter_list, 50)

	page = request.GET.get('page')

	# Calls utils method to append new filters or order_by to the current url
	filter_urls = build_orderby_urls(request.get_full_path(), ['snp_id', 'filter_id', 'filter_result',
	                                                           'filter_cv'])
	try:
		filters = paginator.page(page)
	except PageNotAnInteger:
		filters = paginator.page(1)
	except EmptyPage:
		filters = paginator.page(paginator.num_pages)

	toolbar_max = min(filters.number + 3, paginator.num_pages)
	toolbar_min = max(filters.number - 3, 0)
	return render_to_response('snpdb/filter.html', {"filters": filters,
	                                                "filter_urls": filter_urls,
	                                                "paginator": paginator,
	                                                "toolbar_max": toolbar_max,
	                                                "toolbar_min": toolbar_min})


# Returns the general SNP table view
def snp(request):
	order_by = request.GET.get('order_by', 'snp_id')
	snp_list = SNP.objects.values('snp_id','snp_position', 'result', 'ref_base', 'alt_base',
	                              'heterozygosity', 'quality', 'library', 'chromosome__chromosome_name').order_by(order_by)
	count = len(snp_list)
	paginator = Paginator(snp_list, 50)
	page = request.GET.get('page')

	# Calls utils method to append new filters or order_by to the current url
	filter_urls = build_orderby_urls(request.get_full_path(), ['snp_id', 'snp_position', 'result',
	                                                           'ref_base', 'alt_base', 'heterozygosity',
	                                                           'quality', 'library', 'chromosome__chromosome_name'])
	try:
		snps = paginator.page(page)
	except PageNotAnInteger:
		snps = paginator.page(1)
	except EmptyPage:
		snps = paginator.page(paginator.num_pages)

	toolbar_max = min(snps.number + 3, paginator.num_pages)
	toolbar_min = max(snps.number - 3, 0)

	return render_to_response('snpdb/snp.html', {"snps": snps,
	                                             "count": count,
	                                             "filter_urls": filter_urls,
	                                             "paginator": paginator,
	                                             "toolbar_max": toolbar_max,
	                                             "toolbar_min": toolbar_min})


# Returns the general SNP Type table view.
def snp_type(request):
	order_by = request.GET.get('order_by', 'snptype_id')
	snptype_list = SNP_Type.objects.all().order_by(order_by)
	paginator = Paginator(snptype_list, 50)

	page = request.GET.get('page')

	# Calls utils method to append new filters or order_by to the current url
	filter_urls = build_orderby_urls(request.get_full_path(), ['snptype_id', 'snp_id', 'indel',
	                                                           'deletion', 'is_snp', 'monomorphic',
	                                                           'transition', 'sv'])
	try:
		snptypes = paginator.page(page)
	except PageNotAnInteger:
		snptypes = paginator.page(1)
	except EmptyPage:
		snptypes = paginator.page(paginator.num_pages)

	toolbar_max = min(snptypes.number + 4, paginator.num_pages)
	toolbar_min = max(snptypes.number - 4, 0)

	return render_to_response('snpdb/snptype.html', {"snptypes": snptypes,
	                                                 "filter_urls": filter_urls,
	                                                 "paginator": paginator,
	                                                 "toolbar_max": toolbar_max,
	                                                 "toolbar_min": toolbar_min})


# Returns the general statistics table view.
def statistics(request):
	order_by = request.GET.get('order_by', 'stats_id')
	statistic_list = Statistics.objects.all().order_by(order_by)
	paginator = Paginator(statistic_list, 50)

	page = request.GET.get('page')

	# Calls utils method to append new filters or order_by to the current url
	filter_urls = build_orderby_urls(request.get_full_path(), ['stats_id', 'snp', 'stats_cvterm',
	                                                           'cv_value'])
	try:
		statistic = paginator.page(page)
	except PageNotAnInteger:
		statistic = paginator.page(1)
	except EmptyPage:
		statistic = paginator.page(paginator.num_pages)

	toolbar_max = min(statistic.number + 3, paginator.num_pages)
	toolbar_min = max(statistic.number - 3, 0)

	return render_to_response('snpdb/statistics.html', {"statistic": statistic,
	                                                    "filter_urls": filter_urls,
	                                                    "paginator": paginator,
	                                                    "toolbar_max": toolbar_max,
	                                                    "toolbar_min": toolbar_min})


# Search views
#---------------------------------------------------------------------------------------------------
#todo merge filter views with basic views.
# Returns a view of the Effect table that has been filtered.
def effect_filter(request):
	selection = request.GET.get('att')
	filter_on = request.GET.get('s')
	# current_url = request.get_full_path()
	filter_dict = {}
	filter_dict[str(selection)] = str(filter_on)
	result_list = Effect.objects.all().filter(**filter_dict)

	order_by = request.GET.get('order_by', 'snp')
	result_list = result_list.order_by(order_by)
	paginator = Paginator(result_list, 50)
	page = request.GET.get('page')
	filter_urls = build_orderby_urls(request.get_full_path(), ['snp_id', 'effect', 'effect_class',
	                                                           'effect_string', 'effect_group'])
	try:
		snp_effect = paginator.page(page)
	except PageNotAnInteger:
		snp_effect = paginator.page(1)
	except EmptyPage:
		snp_effect = paginator.page(paginator.num_pages)

	toolbar_max = min(snp_effect.number + 3, paginator.num_pages)
	toolbar_min = max(snp_effect.number - 3, 0)

	return render_to_response('snpdb/effect.html', {"snp_effect": snp_effect,
	                                                "filter_urls": filter_urls,
	                                                "selection": selection,
	                                                "filter_on": filter_on,
	                                                "paginator": paginator,
	                                                "toolbar_max": toolbar_max,
	                                                "toolbar_min": toolbar_min},
	                          context_instance=RequestContext(request))


# Returns a view of the SNP table that has been filtered.
def snp_filter_result(request):
	selection = request.GET.get('att')
	filter_on = request.GET.get('s')
	filter_dict = {}
	filter_dict[str(selection)] = str(filter_on)

	result_list = SNP.objects.values('snp_id','snp_position', 'result', 'ref_base', 'alt_base',
	                                 'heterozygosity', 'quality', 'library', 'chromosome__chromosome_name').filter(**filter_dict)

	order_by = request.GET.get('order_by', 'snp_id')
	result_list = result_list.order_by(order_by)
	filter_urls = build_orderby_urls(request.get_full_path(), ['snp_id', 'snp_position', 'result',
	                                                           'ref_base', 'alt_base', 'heterozygosity',
	                                                           'quality', 'library', 'chromosome__chromosome_name'])
	paginator = Paginator(result_list, 50)
	page = request.GET.get('page')

	try:
		snps = paginator.page(page)
	except PageNotAnInteger:
		snps = paginator.page(1)
	except EmptyPage:
		snps = paginator.page(paginator.num_pages)

	toolbar_max = min(snps.number + 3, paginator.num_pages)
	toolbar_min = max(snps.number - 3, 0)

	return render_to_response('snpdb/snp.html', {"snps": snps,
	                                             "filter_urls": filter_urls,
	                                             "selection": selection,
	                                             "filter_on": filter_on,
	                                             "paginator": paginator,
	                                             "toolbar_max": toolbar_max,
	                                             "toolbar_min": toolbar_min},
	                          context_instance=RequestContext(request))


# Returns a view of the Filter table that has been filtered.
def filter_filter(request):
	selection = request.GET.get('att')
	filter_on = request.GET.get('s')
	filter_dict = {}
	filter_dict[str(selection)] = str(filter_on)
	result_list = Filter.objects.all().filter(**filter_dict)

	order_by = request.GET.get('order_by', 'snp')
	result_list = result_list.order_by(order_by)
	paginator = Paginator(result_list, 50)
	page = request.GET.get('page')
	filter_urls = build_orderby_urls(request.get_full_path(), ['snp_id', 'filter_id', 'filter_result',
	                                                           'filter_cv'])
	try:
		filters = paginator.page(page)
	except PageNotAnInteger:
		filters = paginator.page(1)
	except EmptyPage:
		filters = paginator.page(paginator.num_pages)

	toolbar_max = min(filters.number + 3, paginator.num_pages)
	toolbar_min = max(filters.number - 3, 0)

	return render_to_response('snpdb/filter.html', {"filters": filters,
	                                                "filter_urls": filter_urls,
	                                                "selection": selection,
	                                                "filter_on": filter_on,
	                                                "paginator": paginator,
	                                                "toolbar_max": toolbar_max,
	                                                "toolbar_min": toolbar_min})


# Returns a view of the SNP Type table that has been filtered.
def snptype_filter(request):
	selection = request.GET.get('att')
	filter_on = request.GET.get('s')
	filter_dict = {}
	filter_dict[str(selection)] = str(filter_on)

	result_list = SNP_Type.objects.all().filter(**filter_dict)

	order_by = request.GET.get('order_by', 'snp')
	result_list = result_list.order_by(order_by)
	paginator = Paginator(result_list, 50)
	page = request.GET.get('page')
	filter_urls = build_orderby_urls(request.get_full_path(), ['snptype_id', 'snp_id', 'indel',
	                                                           'deletion', 'is_snp', 'monomorphic',
	                                                           'transition', 'sv'])
	try:
		snptypes = paginator.page(page)
	except PageNotAnInteger:
		snptypes = paginator.page(1)
	except EmptyPage:
		snptypes = paginator.page(paginator.num_pages)

	toolbar_max = min(snptypes.number + 4, paginator.num_pages)
	toolbar_min = max(snptypes.number - 4, 0)

	return render_to_response('snpdb/snptype.html', {"snptypes": snptypes,
	                                                 "filter_urls": filter_urls,
	                                                 "selection": selection,
	                                                 "filter_on": filter_on,
	                                                 "paginator": paginator,
	                                                 "toolbar_max": toolbar_max,
	                                                 "toolbar_min": toolbar_min})


# Returns a view of the Statistics table that has been filtered.
def statistics_filter(request):
	selection = request.GET.get('att')
	filter_on = request.GET.get('s')
	filter_dict = {}
	filter_dict[str(selection)] = str(filter_on)

	result_list = Statistics.objects.all().filter(**filter_dict)

	order_by = request.GET.get('order_by', 'snp')
	result_list = result_list.order_by(order_by)
	paginator = Paginator(result_list, 50)
	page = request.GET.get('page')
	filter_urls = build_orderby_urls(request.get_full_path(), ['stats_id', 'snp', 'stats_cvterm',
	                                                           'cv_value'])
	try:
		statistic = paginator.page(page)
	except PageNotAnInteger:
		statistic = paginator.page(1)
	except EmptyPage:
		statistic = paginator.page(paginator.num_pages)

	toolbar_max = min(statistic.number + 4, paginator.num_pages)
	toolbar_min = max(statistic.number - 4, 0)

	return render_to_response('snpdb/statistics.html', {"statistic": statistic,
	                                                    "filter_urls": filter_urls,
	                                                    "selection": selection,
	                                                    "filter_on": filter_on,
	                                                    "paginator": paginator,
	                                                    "toolbar_max": toolbar_max,
	                                                    "toolbar_min": toolbar_min})


# Query views.
# --------------------------------------------------------------------------------------
# Displays the search page to compare snps across libraries
def compare_gene_lib(request):
	genes = Effect.objects.values('effect_string').filter(effect=6).filter(effect_class=("NON_SYNONYMOUS_CODING" or "SYNONYMOUS_CODING")).distinct().order_by('effect_string')
	count = len(genes)
	paginator = Paginator(genes, 120)

	page = request.GET.get('page')
	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)
	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)

	return render_to_response('snpdb/compare_gene_library.html', {"results": results,
	                                                              "count": count,
	                                                              "paginator": paginator,
	                                                              "toolbar_max": toolbar_max,
	                                                              "toolbar_min": toolbar_min})


# Returns the comparison of a gene across specific libraries.
def compare_gene_lib_filter(request):
	order_by = request.GET.get('order_by', 'librarycode')
	gene = request.GET.get('s')
	result_list = Library.objects.values('library_id', 'librarycode', 'organism_id', 'organism__organismcode', 'organism__genome__genome_id', 'organism__genome__version').filter(organism_id=Genome.objects.values_list('organism_id', flat=True).filter(genome_id=Feature.objects.values_list('genome', flat=True).filter(geneid=gene).distinct())).order_by(order_by)

	page = request.GET.get('page')
	filter_urls = build_orderby_urls(request.get_full_path(), ['library_id', 'librarycode', 'organism_id', 'organism__organismcode', 'organism__genome__genome_id', 'organism__genome__version'])
	count = len(filter_urls)
	paginator = Paginator(result_list, 50)
	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)

	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)

	return render_to_response('snpdb/compare_gene_library_filter.html', {"results": results,
	                                                                     "gene": gene,
	                                                                     "count": count,
	                                                                     "filter_urls": filter_urls,
	                                                                     "toolbar_max": toolbar_max,
	                                                                     "toolbar_min": toolbar_min })


def compare_gene_lib_filter_results_effect(request):
	# order_by = request.GET.get('order_by', 'library__librarycode')
	gene = request.GET.get('s')
	library = request.GET.getlist('check')
	cds_fmin = Feature.objects.values_list('fmin', flat=True).filter(geneid=gene, featuretype='CDS')[0]
	cds_fmax = Feature.objects.values_list('fmax', flat=True).filter(geneid=gene, featuretype='CDS')[0]
	fmin = Feature.objects.filter(geneid=gene).filter(featuretype='gene').values('fmin')[0]
	fmax = Feature.objects.filter(geneid=gene).filter(featuretype='gene').values('fmax')[0]

	result_list = SNP.objects.filter(effect__effect_id=6, effect__effect_string__exact=gene,
	                                 effect__effect_class__endswith='SYNONYMOUS_CODING'.decode('utf-8'),
	                                 library__librarycode__in=library).values('library', 'library__librarycode', 'snp_id',
	                                                                          'snp_position', 'ref_base', 'alt_base',
	                                                                          'heterozygosity', 'quality',
	                                                                          'chromosome__chromosome_name', 'effect__effect_string',
	                                                                          'effect__effect_class', 'effect__effect')
	snp_group = []
	library_group = []
	max_snps = 0
	count = 0
	for each in result_list:
		snp_position = each['snp_position']
		library = each['library__librarycode']
		if snp_position in snp_group:
			count += 1
			pass
		else:
			snp_group.append(snp_position)
			count = 1
			pass
		if count > max_snps:
			max_snps = count
			count = 0
		if library in library_group:
			pass
		else:
			library_group.append(library)
	paginator = Paginator(result_list, 50)
	page = request.GET.get('page')
	filter_urls = build_orderby_urls(request.get_full_path(), ['snp_id', 'snp_position', 'ref_base', 'alt_base', 'library__librarycode'])
	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)

	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)

	return render_to_response('snpdb/compare_gene_library_filter_result.html', {"results": results,
	                                                                            "gene": gene,
	                                                                            "cds_fmin": cds_fmin,
	                                                                            "cds_fmax": cds_fmax,
	                                                                            "fmin": fmin,
	                                                                            "fmax": fmax,
	                                                                            "count": len(snp_group),
	                                                                            "library_group": library_group,
	                                                                            "snp_group": snp_group,
	                                                                            "max_snps": range(max_snps),
	                                                                            "filter_urls": filter_urls,
	                                                                            "toolbar_max": toolbar_max,
	                                                                            "toolbar_min": toolbar_min})


# Returns the list of genes found within the selected libraries.
# todo need to change view so that all library snps align. Look at gene LdBPK_292260.1 as an example (across all libs).
# todo need to change so that it references effect table rather than feature table
def compare_gene_lib_filter_results(request):
	order_by = request.GET.get('order_by', 'library__librarycode')
	gene = request.GET.get('s')
	library = request.GET.getlist('check')
	cds_fmin = Feature.objects.values_list('fmin', flat=True).filter(geneid=gene, featuretype='CDS')[0]
	cds_fmax = Feature.objects.values_list('fmax', flat=True).filter(geneid=gene, featuretype='CDS')[0]
	fmin = Feature.objects.filter(geneid=gene).filter(featuretype='gene').values('fmin')[0]
	fmax = Feature.objects.filter(geneid=gene).filter(featuretype='gene').values('fmax')[0]
	result_list = SNP.objects.values('snp_id', 'snp_position', 'ref_base',
	                                 'alt_base', 'library__librarycode').filter(library__librarycode__in=library,
	                                                                            snp_position__range=(Feature.objects.values_list('fmin', flat=True).filter(geneid=gene).filter(featuretype='gene')[0],
	                                                                                                 Feature.objects.values_list('fmax', flat=True).filter(geneid=gene).filter(featuretype='gene')[0]),
	                                                                            chromosome__chromosome_name=Feature.objects.values_list('chromosome', flat=True).filter(geneid=gene).filter(featuretype='gene')[0]).order_by(order_by)

	snp_group = []
	library_group = []
	max_snps = 0
	count = 0
	for each in result_list:
		snp_position = each['snp_position']
		library = each['library__librarycode']
		if snp_position in snp_group:
			count += 1
			pass
		else:
			snp_group.append(snp_position)
			count = 1
			pass
		if count > max_snps:
			max_snps = count
			count = 0
		if library in library_group:
			pass
		else:
			library_group.append(library)
	paginator = Paginator(result_list, 50)
	page = request.GET.get('page')
	filter_urls = build_orderby_urls(request.get_full_path(), ['snp_id', 'snp_position', 'ref_base', 'alt_base', 'library__librarycode'])
	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)

	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)

	return render_to_response('snpdb/compare_gene_library_filter_result.html', {"results": results,
	                                                                            "gene": gene,
	                                                                            "cds_fmin": cds_fmin,
	                                                                            "cds_fmax": cds_fmax,
	                                                                            "fmin": fmin,
	                                                                            "fmax": fmax,
	                                                                            "count": len(snp_group),
	                                                                            "library_group": library_group,
	                                                                            "snp_group": snp_group,
	                                                                            "max_snps": range(max_snps),
	                                                                            "filter_urls": filter_urls,
	                                                                            "toolbar_max": toolbar_max,
	                                                                            "toolbar_min": toolbar_min})


# Returns information about a gene through the feature table.
def gene_feature(request):
	geneid = request.GET.get('geneid')
	order_by = request.GET.get('order_by', 'geneid')

	feature = Feature.objects.all().filter(geneid=geneid, featuretype='gene').order_by(order_by)
	paginator = Paginator(feature, 50)
	page = request.GET.get('page')
	filter_urls = build_orderby_urls(request.get_full_path(), ['snp_id', 'snp_position', 'ref_base',
	                                                           'alt_base', 'library__librarycode'])
	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)

	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)

	return render_to_response('snpdb/gene_feature.html', {"geneid": geneid,
	                                                      "results": results,
	                                                      "filter_urls": filter_urls,
	                                                      "toolbar_max": toolbar_max,
	                                                      "toolbar_min": toolbar_min,})


# The search view for the user to input a gene. Lists all gene ids for the user to choose from.
def gene_snps(request):
	genes = Effect.objects.values('effect_string').filter(effect=6).filter(effect_class=("NON_SYNONYMOUS_CODING" or "SYNONYMOUS_CODING")).distinct().order_by('effect_string')
	paginator = Paginator(genes, 120)

	page = request.GET.get('page')
	try:
		genes = paginator.page(page)
	except PageNotAnInteger:
		genes = paginator.page(1)
	except EmptyPage:
		genes = paginator.page(paginator.num_pages)
	toolbar_max = min(genes.number + 4, paginator.num_pages)
	toolbar_min = max(genes.number - 4, 0)

	return render_to_response('snpdb/gene_to_snp.html', {"genes": genes,
	                                                     "paginator": paginator,
	                                                     "toolbar_max": toolbar_max,
	                                                     "toolbar_min": toolbar_min})


# Returns all snps found within the gene location regardless of library.
def gene_snps_filter(request):
	flanks = int(request.GET.get('f'))
	order_by = request.GET.get('order_by', 'library__librarycode')
	gene = request.GET.get('s')
	fmin = Feature.objects.values_list('fmin', flat=True).filter(geneid=gene).filter(featuretype='gene')[0]
	fmax = Feature.objects.values_list('fmax', flat=True).filter(geneid=gene).filter(featuretype='gene')[0]
	try:
		cds_fmin = Feature.objects.values_list('fmin', flat=True).filter(geneid=gene, featuretype='CDS')[0]
		cds_fmax = Feature.objects.values_list('fmax', flat=True).filter(geneid=gene, featuretype='CDS')[0]
	except IndexError:
		print "There are no CDS regions associated with this gene."
		cds_fmin = 0
		cds_fmax = 0
		pass
	# chromosome = Feature.objects.values_list('chromosome', flat=True).filter(geneid=gene).filter(featuretype='gene')[0]
	result_list = SNP.objects.values('library__librarycode', 'result_id',
	                                 'chromosome__chromosome_name', 'snp_id',
	                                 'snp_position', 'ref_base',
	                                 'alt_base').filter(snp_position__range=((Feature.objects.values_list('fmin', flat=True).filter(geneid=gene).filter(featuretype='gene')[0])+flanks,
	                                                                         (Feature.objects.values_list('fmax', flat=True).filter(geneid=gene).filter(featuretype='gene')[0])+flanks),
	                                                    chromosome__chromosome_name=Feature.objects.values_list('chromosome', flat=True).filter(geneid=gene).filter(featuretype='gene')[0]).order_by(order_by)
	count = result_list.count()
	paginator = Paginator(result_list, 50)
	page = request.GET.get('page')
	filter_urls = build_orderby_urls(request.get_full_path(), ['library__librarycode', 'result_id',
	                                                           'chromosome__chromosome_name', 'snp_id',
	                                                           'snp_position', 'ref_base', 'alt_base'])
	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)

	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)

	return render_to_response('snpdb/snps_in_gene_filter.html', {"results": results,
	                                                             "filter_urls": filter_urls,
	                                                             "paginator": paginator,
	                                                             "toolbar_max": toolbar_max,
	                                                             "toolbar_min": toolbar_min,
	                                                             "cds_fmin": cds_fmin,
	                                                             "cds_fmax": cds_fmax,
	                                                             "fmin": fmin,
	                                                             "fmax": fmax,
	                                                             "gene": gene,
	                                                             "count": count})


# Returns the search page to query both a library/gene combination for snps.
def library_gene_snps(request):
	gene = request.GET.get('s')
	library = request.GET.get('lib')
	lib_list = Library.objects.values('librarycode')
	page = request.GET.get('page')
	paginator = Paginator(lib_list, 120)

	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)
	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)
	return render_to_response('snpdb/library_to_snp.html', {"results": results,
	                                                        "gene": gene,
	                                                        "library": library,
	                                                        "paginator": paginator,
	                                                        "toolbar_max": toolbar_max,
	                                                        "toolbar_min": toolbar_min})


# Returns the snps found within a specific library and gene.
def library_gene_snps_filter(request):
	order_by = request.GET.get('order_by', 'library__librarycode')
	gene = request.GET.get('s')
	library = request.GET.get('lib')
	cds_fmin = Feature.objects.values_list('fmin', flat=True).filter(geneid=gene, featuretype='CDS')[0]
	cds_fmax = Feature.objects.values_list('fmax', flat=True).filter(geneid=gene, featuretype='CDS')[0]
	fmin = Feature.objects.values_list('fmin', flat=True).filter(geneid=gene).filter(featuretype='gene')[0]
	fmax = Feature.objects.values_list('fmax', flat=True).filter(geneid=gene).filter(featuretype='gene')[0]
	result_list = SNP.objects.values('library__librarycode', 'result_id',
	                                 'chromosome__chromosome_name', 'snp_id',
	                                 'snp_position', 'ref_base', 'alt_base',
	                                 'quality', 'heterozygosity').filter(snp_position__range=(Feature.objects.values_list('fmin', flat=True).filter(geneid=gene).filter(featuretype='gene')[0],
	                                                                                          Feature.objects.values_list('fmax', flat=True).filter(geneid=gene).filter(featuretype='gene')[0]),
	                                                                     library__librarycode=library,
	                                                                     chromosome__chromosome_name=Feature.objects.values_list('chromosome', flat=True).filter(geneid=gene).filter(featuretype='gene')[0]).order_by(order_by)
	count = result_list.count()
	page = request.GET.get('page')
	filter_urls = build_orderby_urls(request.get_full_path(), ['library', 'result_id', 'gene', 'result_id',
	                                                           'chromosome__chromosome_name', 'snp_id',
	                                                           'snp_position', 'ref_base', 'alt_base',
	                                                           'quality', 'heterozygosity'])
	paginator = Paginator(result_list, 50)
	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)
		print "Error"

	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)

	return render_to_response('snpdb/library_to_snp_filter.html', {"results": results,
	                                                               "gene": gene,
	                                                               "library": library,
	                                                               "cds_fmin": cds_fmin,
	                                                               "cds_fmax": cds_fmax,
	                                                               "fmin": fmin,
	                                                               "fmax": fmax,
	                                                               "filter_urls": filter_urls,
	                                                               "paginator": paginator,
	                                                               "toolbar_max": toolbar_max,
	                                                               "toolbar_min": toolbar_min,
	                                                               "count": count})


# Returns a summary of the number of snps found in each library.
def library_snp_summary(request):
	order_by = request.GET.get('order_by', 'library')
	results = SNP.objects.values('library__librarysize',
	                             'library_id',
	                             'library__librarycode').distinct().annotate(num_snps=Count('snp_id'),
	                                                                         hetero=BooleanSum('heterozygosity'),
	                                                                         indel=BooleanSum('snp_type__indel'),
	                                                                         trans=BooleanSum('snp_type__transition')).order_by(order_by)
	result_list = results.order_by(order_by)
	paginator = Paginator(result_list, 50)
	page = request.GET.get('page')
	count = len(results)

	# Calls utils method to append new filters or order_by to the current url
	filter_urls = build_orderby_urls(request.get_full_path(), ['library__library_id', 'library__librarycode', 'snp_id', 'num_snps', 'hetero', 'homo', 'indel', 'trans', 'snp_density'])

	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)

	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)

	return render_to_response('snpdb/library_snp_summary.html', {"results": results,
	                                                             "count": count,
	                                                             "filter_urls": filter_urls,
	                                                             "paginator": paginator,
	                                                             "toolbar_max": toolbar_max,
	                                                             "toolbar_min": toolbar_min })


# Returns all snps found within a library using the effect table.
def library_snps(request):
	order_by = request.GET.get('order_by', 'snp_id').encode("ascii")
	library = request.GET.get('lib')
	count = request.GET.get('count')
	selection = request.GET.get('att')
	filter_on = request.GET.get('s')
	filter_dict = {}
	if selection:
		filter_dict[str(selection)] = str(filter_on)
	if filter_dict:
		if selection == 'effect__effect_string':
			results = SNP.objects.filter(effect__effect_id=6, effect__effect_string__exact=filter_on.decode('utf-8'),
			                             effect__effect_class__endswith='SYNONYMOUS_CODING'.decode('utf-8'),
			                             library__librarycode=library).values('library', 'library__librarycode', 'snp_id',
			                                                                  'snp_position', 'ref_base', 'alt_base',
			                                                                  'heterozygosity', 'quality',
			                                                                  'chromosome__chromosome_name', 'effect__effect_string',
			                                                                  'effect__effect_class', 'effect__effect')
		else:
			results = SNP.objects.filter(**filter_dict).filter(library__librarycode=library).values('library', 'library__librarycode', 'snp_id',
			                                                                                        'snp_position', 'ref_base', 'alt_base',
			                                                                                        'heterozygosity', 'quality',
			                                                                                        'chromosome__chromosome_name', 'effect__effect_string',
			                                                                                        'effect__effect_class', 'effect__effect')
	else:
		results = SNP.objects.values('library', 'library__librarycode', 'snp_id',
		                             'snp_position', 'ref_base', 'alt_base',
		                             'heterozygosity', 'quality',
		                             'chromosome__chromosome_name', 'effect__effect_string',
		                             'effect__effect_class', 'effect__effect')
	sorted_snp_dict = genes_from_effect(results, library, order_by)
	paginator = Paginator(sorted_snp_dict, 100)
	page = request.GET.get('page')

	# Calls utils method to append new filters or order_by to the current url
	filter_urls = build_orderby_urls(request.get_full_path(), ['library', 'library__librarycode', 'snp_id',
	                                                           'snp_position', 'ref_base', 'alt_base',
	                                                           'heterozygosity', 'quality',
	                                                           'chromosome__chromosome_name',
	                                                           'effect__effect_string'])
	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)

	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)

	return render_to_response('snpdb/library_snps.html', {"results": results,
	                                                      "library": library,
	                                                      "order_by": order_by,
	                                                      "filter_urls": filter_urls,
	                                                      "paginator": paginator,
	                                                      "toolbar_max": toolbar_max,
	                                                      "toolbar_min": toolbar_min,
	                                                      "count": count})


def genes_from_effect(results, library, order_by):
	snp_dict = {}
	for each in results:
		# print each
		current_genes = []
		if each['library__librarycode'] == library:
			if empty_effect(each['effect__effect']) or each['effect__effect'] == 6:
				# if empty_effect(each['effect__effect_class']) or (each['effect__effect_class'] == ('NON_SYNONYMOUS_CODING' or 'SYNONYMOUS_CODING')):
				if each['snp_id'] in snp_dict:
					for k, v in snp_dict[each['snp_id']].iteritems():
						if k == 'effect__effect_string':
							if type(v) is list:
								for x in v:
									current_genes.append(str(x).decode('UTF8').strip())
							else:
								current_genes.append(str(v).decode('UTF8'))
					if each['effect__effect_string'] in current_genes:
						pass
					elif snp_dict[each['snp_id']]['effect__effect_string'] == 'None':
						snp_dict[each['snp_id']] = each
					else:
						current_genes.append(str(each['effect__effect_string']).strip())
						each['effect__effect_string'] = current_genes
						snp_dict[each['snp_id']] = each
				else:
					snp_dict[each['snp_id']] = each
				# else:
				#     if each['snp_id'] in snp_dict:
				#         pass
				#     else:
				#         each["effect__effect_class"] = 'None'
				#         each["effect__effect_string"] = 'None'
				#         each["effect__effect"] = 'None'
				#         snp_dict[each['snp_id']] = each
			else:
				if each['snp_id'] in snp_dict:
					pass
				else:
					each["effect__effect_class"] = 'None'
					each["effect__effect_string"] = 'None'
					each["effect__effect"] = 'None'
					snp_dict[each['snp_id']] = each
	sorted_snp_dict = sorted(snp_dict.items(), key=lambda x: x[1][order_by])
	return sorted_snp_dict


# Returns snps found in a library and chromosome.
def library_chromosome_snps_filter(request):
	chromosome = request.GET.get('s')
	library = request.GET.get('lib')
	order_by = request.GET.get('order_by', 'library__librarycode')
	result_list = SNP.objects.values('library__librarycode', 'result_id',
	                                 'chromosome__chromosome_name', 'snp_id',
	                                 'snp_position', 'ref_base', 'alt_base',
	                                 'quality', 'heterozygosity').filter(snp_position__range=(Feature.objects.values_list('fmin', flat=True).filter(chromosome=chromosome).filter(featuretype='gene')[0],
	                                                                                          Feature.objects.values_list('fmax', flat=True).filter(chromosome=chromosome).filter(featuretype='gene')[0]),
	                                                                     library__librarycode=library, chromosome__chromosome_name=Feature.objects.values_list('chromosome', flat=True).filter(chromosome=chromosome).filter(featuretype='gene')[0]).order_by(order_by)
	count = result_list.count()
	page = request.GET.get('page')
	filter_urls = build_orderby_urls(request.get_full_path(), ['library__librarycode', 'result_id',
	                                                           'chromosome__chromosome_name', 'snp_id',
	                                                           'snp_position', 'ref_base', 'alt_base',
	                                                           'quality', 'heterozygosity'])
	paginator = Paginator(result_list, 50)
	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)
		print "Error"

	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)

	return render_to_response('snpdb/library_chromosome_filter.html', {"results": results,
	                                                                   "chromosome": chromosome,
	                                                                   "library": library,
	                                                                   "filter_urls": filter_urls,
	                                                                   "paginator": paginator,
	                                                                   "toolbar_max": toolbar_max,
	                                                                   "toolbar_min": toolbar_min,
	                                                                   "count": count})


# Displays the search page for a snp summary by library and chromosome level.
def chromosome_library_snp_summary(request):
	libraries = Library.objects.values('librarycode').distinct().order_by('librarycode')
	paginator = Paginator(libraries, 120)

	page = request.GET.get('page')
	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)
	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)

	return render_to_response('snpdb/chromosome_library_snp_summary.html', {"results": results,
	                                                                        "paginator": paginator,
	                                                                        "toolbar_max": toolbar_max,
	                                                                        "toolbar_min": toolbar_min})


# Returns a chromosome level summary for an individual library.
def chromosome_library_snp_summary_filter(request):
	order_by = request.GET.get('order_by', 'chromosome__chromosome_name')
	library = request.GET.get('lib')
	results = SNP.objects.values('chromosome__chromosome_name', 'library__librarysize',
	                             'library_id', 'library__librarycode').filter(library__librarycode=library).annotate(num_snps=Count('snp_id'),
	                                                                                                                 hetero=BooleanSum('heterozygosity'),
	                                                                                                                 indel=BooleanSum('snp_type__indel'),
	                                                                                                                 trans=BooleanSum('snp_type__transition'))
	result_list = results.order_by(order_by)
	print result_list
	paginator = Paginator(result_list, 50)
	page = request.GET.get('page')

	# Calls utils method to append new filters or order_by to the current url
	filter_urls = build_orderby_urls(request.get_full_path(), ['chromosome__chromosome_name', 'library__librarysize', 'library_id', 'library__librarycode',
	                                                           'num_snps', 'hetero', 'trans', 'indel'])

	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)

	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)

	return render_to_response('snpdb/chromosome_library_snp_summary_filter.html', {"results": results,
	                                                                               "filter_urls": filter_urls,
	                                                                               "paginator": paginator,
	                                                                               "toolbar_max": toolbar_max,
	                                                                               "toolbar_min": toolbar_min})


# Returns the snps found within a library and chromosome
def library_chromosome_snps(request):
	chromosomes = Chromosome.objects.values('chromosome_name').distinct().order_by('chromosome_name')
	page = request.GET.get('page')

	paginator = Paginator(chromosomes, 50)

	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)
	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)

	return render_to_response('snpdb/library_chromosome_snp.html', {"results": results,
	                                                                "paginator": paginator,
	                                                                "toolbar_max": toolbar_max,
	                                                                "toolbar_min": toolbar_min})


# todo change to access genes through the Effect table.
# Returns a full list of genes found within a specific library. Currently connects through the feature table.
def gene_list(request):
	order_by = request.GET.get('order_by', 'chromosome')
	library = request.GET.get('lib')
	results = Feature.objects.values('geneid', 'fmin', 'fmax', 'chromosome').filter(featuretype='gene',
	                                                                                genome__organism__library__librarycode=library).order_by(order_by)
	count = len(results)

	paginator = Paginator(results, 200)
	page = request.GET.get('page')

	filter_urls = build_orderby_urls(request.get_full_path(), ['geneid', 'chromosome', 'fmin', 'fmax'])
	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)
	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)

	return render_to_response('snpdb/gene_list.html', {"results": results,
	                                                   "library": library,
	                                                   "count": count,
	                                                   "filter_urls": filter_urls,
	                                                   "paginator": paginator,
	                                                   "toolbar_max": toolbar_max,
	                                                   "toolbar_min": toolbar_min})


# View to search a list of genes for snps.
def multi_gene_snps(request):
	genes = Effect.objects.values('effect_string').filter(effect=6).filter(effect_class=("NON_SYNONYMOUS_CODING" or "SYNONYMOUS_CODING")).distinct().order_by('effect_string')
	paginator = Paginator(genes, 120)

	page = request.GET.get('page')
	try:
		genes = paginator.page(page)
	except PageNotAnInteger:
		genes = paginator.page(1)
	except EmptyPage:
		genes = paginator.page(paginator.num_pages)
	toolbar_max = min(genes.number + 4, paginator.num_pages)
	toolbar_min = max(genes.number - 4, 0)

	return render_to_response('snpdb/multi_gene_snps.html', {"genes": genes,
	                                                         "paginator": paginator,
	                                                         "toolbar_max": toolbar_max,
	                                                         "toolbar_min": toolbar_min})


# Returns snps found within a list of genes. Does not consider library.
def multi_gene_snps_filter(request):
	order_by = request.GET.get('order_by', 'effect__effect_string')
	gene = request.GET.get('s')
	genes = gene.split()

	result_list = SNP.objects.filter(effect__effect_id=6, effect__effect_string__in=genes,
	                                 effect__effect_class__endswith='SYNONYMOUS_CODING'.decode('utf-8')).values('library', 'library__librarycode', 'snp_id',
	                                                                                                            'snp_position', 'ref_base', 'alt_base',
	                                                                                                            'heterozygosity', 'quality',
	                                                                                                            'chromosome__chromosome_name', 'effect__effect_string',
	                                                                                                            'effect__effect_class', 'effect__effect', 'result_id').order_by(order_by)

	count = result_list.count()
	paginator = Paginator(result_list, 50)
	page = request.GET.get('page')
	filter_urls = build_orderby_urls(request.get_full_path(), ['library', 'library__librarycode', 'snp_id',
	                                                           'snp_position', 'ref_base', 'alt_base',
	                                                           'heterozygosity', 'quality',
	                                                           'chromosome__chromosome_name', 'effect__effect_string',
	                                                           'effect__effect_class', 'effect__effect', 'result_id'])
	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)

	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)

	return render_to_response('snpdb/multi_gene_snps_filter.html', {"results": results,
	                                                                "filter_urls": filter_urls,
	                                                                "paginator": paginator,
	                                                                "toolbar_max": toolbar_max,
	                                                                "toolbar_min": toolbar_min,
	                                                                "genes": genes,
	                                                                "count": count})


def multi_gene_library_snps(request):
	libraries = Library.objects.values('librarycode').order_by('librarycode')
	# print len(libraries)
	genes = Effect.objects.values('effect_string').filter(effect=6).filter(effect_class=("NON_SYNONYMOUS_CODING" or
	                                                                                     "SYNONYMOUS_CODING")).distinct().order_by('effect_string')

	paginator = Paginator(genes, 50)
	page = request.GET.get('page')
	try:
		genes = paginator.page(page)
	except PageNotAnInteger:
		genes = paginator.page(1)
	except EmptyPage:
		genes = paginator.page(paginator.num_pages)

	toolbar_max = min(genes.number + 4, paginator.num_pages)
	toolbar_min = max(genes.number - 4, 0)

	return render_to_response('snpdb/multi_gene_snps_library.html', {"genes": genes,
	                                                                 "libraries": libraries,
	                                                                 "paginator": paginator,
	                                                                 "toolbar_max": toolbar_max,
	                                                                 "toolbar_min": toolbar_min})


def multi_gene_library_snps_filter(request):
	order_by = request.GET.get('order_by', 'effect__effect_string')
	gene = request.GET.get('s')
	libraries = request.GET.getlist('check')
	genes = gene.split()
	# libraries = library.split()

	result_list = SNP.objects.filter(effect__effect_id=6, effect__effect_string__in=genes,
	                                 library__librarycode__in=libraries,
	                                 effect__effect_class__endswith='SYNONYMOUS_CODING'.decode('utf-8')).values('library', 'library__librarycode', 'snp_id',
	                                                                                                            'snp_position', 'ref_base', 'alt_base',
	                                                                                                            'heterozygosity', 'quality',
	                                                                                                            'chromosome__chromosome_name', 'effect__effect_string',
	                                                                                                            'effect__effect_class', 'effect__effect', 'result_id').order_by(order_by)

	count = result_list.count()
	paginator = Paginator(result_list, 50)
	page = request.GET.get('page')
	filter_urls = build_orderby_urls(request.get_full_path(), ['library', 'library__librarycode', 'snp_id',
	                                                           'snp_position', 'ref_base', 'alt_base',
	                                                           'heterozygosity', 'quality',
	                                                           'chromosome__chromosome_name', 'effect__effect_string',
	                                                           'effect__effect_class', 'effect__effect', 'result_id'])
	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)

	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)

	return render_to_response('snpdb/multi_gene_snps__library_filter.html', {"results": results,
	                                                                         "filter_urls": filter_urls,
	                                                                         "paginator": paginator,
	                                                                         "toolbar_max": toolbar_max,
	                                                                         "toolbar_min": toolbar_min,
	                                                                         "genes": genes,
	                                                                         "count": count})


# Displays the search page to compare two libraries for unique and similar snps.
def compare_two_libraries(request):
	lib_list = Library.objects.values('librarycode')
	page = request.GET.get('page')
	paginator = Paginator(lib_list, 120)

	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)
	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)
	return render_to_response('snpdb/compare_two_libraries.html', {"results": results,
	                                                               "paginator": paginator,
	                                                               "toolbar_max": toolbar_max,
	                                                               "toolbar_min": toolbar_min})


#todo add googlecharts to show pie chart of impact types
#todo add a link to shared snps.
# Uses bcftools to identify snps that are unique between multiple libraries. This information is organized by impact type.
def difference_two_libraries(request):
	library1 = request.GET.get('lib1')
	library2 = request.GET.get('lib2')
	dir = os.path.abspath(os.path.dirname(__file__))
	vcf_path = os.path.join(dir, 'vcf_files/')
	path = os.path.join(vcf_path, 'bcftools_isec_snpEff_%s_%s_%s' % (library1, library2, datetime.datetime.utcnow().strftime("%Y-%m-%d")))
	if os.path.isdir(path):
		print "file already present"
		pass
	else:
		print "initial analysis being ran"
		test = subprocess.check_call(["""bcftools isec %s/%s_gatk.snpEff.vcf.gz %s/%s_gatk.snpEff.vcf.gz -p %s""" % (vcf_path, library1, vcf_path, library2, path)],
		                             shell=True)
	cmd = """cat %s/0000.vcf | cut -f 8 | tr ";" "\n" | grep ^EFF= | cut -f 2 -d = | tr "," "\n" | grep %s | wc -l"""
	modifier = subprocess.Popen(cmd % (path, "MODIFIER"), shell=True, stdout=subprocess.PIPE)
	moderate = subprocess.Popen(cmd % (path, "MODERATE"), shell=True, stdout=subprocess.PIPE)
	high = subprocess.Popen(cmd % (path, "HIGH"), shell=True, stdout=subprocess.PIPE)
	low = subprocess.Popen(cmd % (path, "LOW"), shell=True, stdout=subprocess.PIPE)
	total = subprocess.Popen("""grep ^[^#] %s/0000.vcf | wc -l""" % path, shell=True, stdout=subprocess.PIPE)
	counts = [high.communicate()[0].strip(), moderate.communicate()[0].strip(), low.communicate()[0].strip(), modifier.communicate()[0].strip(), total.communicate()[0].strip()]


	low_counts = defaultdict(int)
	high_counts = defaultdict(int)
	moderate_counts = defaultdict(int)
	modifier_counts = defaultdict(int)
	for each in low_effects:
		count_effect_cmd = """cat %s/0000.vcf| cut -f 8 | tr ";" "\n" | grep ^EFF= | cut -f 2 -d = | tr "," "\n" | grep %s | wc -l"""
		count_effect = subprocess.Popen(count_effect_cmd % (path, each), shell=True, stdout=subprocess.PIPE)
		count = count_effect.communicate()[0]
		low_counts[each] = count.strip()
	for each in moderate_effects:
		count_effect_cmd = """cat %s/0000.vcf | cut -f 8 | tr ";" "\n" | grep ^EFF= | cut -f 2 -d = | tr "," "\n" | grep %s | wc -l"""
		count_effect = subprocess.Popen(count_effect_cmd % (path, each), shell=True, stdout=subprocess.PIPE)
		count = count_effect.communicate()[0]
		moderate_counts[each] = count.strip()
	for each in modifier_effects:
		count_effect_cmd = """cat %s/0000.vcf | cut -f 8 | tr ";" "\n" | grep ^EFF= | cut -f 2 -d = | tr "," "\n" | grep %s | wc -l"""
		count_effect = subprocess.Popen(count_effect_cmd % (path, each), shell=True, stdout=subprocess.PIPE)
		count = count_effect.communicate()[0]
		modifier_counts[each] = count.strip()
	for each in high_effects:
		count_effect_cmd = """cat %s/0000.vcf | cut -f 8 | tr ";" "\n" | grep ^EFF= | cut -f 2 -d = | tr "," "\n" | grep %s | wc -l"""
		count_effect = subprocess.Popen(count_effect_cmd % (path, each), shell=True, stdout=subprocess.PIPE)
		count = count_effect.communicate()[0]
		high_counts[each] = count.strip()


	cmd2 = """cat %s/0001.vcf | cut -f 8 | tr ";" "\n" | grep ^EFF= | cut -f 2 -d = | tr "," "\n" | grep %s | wc -l"""
	modifier2 = subprocess.Popen(cmd2 % (path, "MODIFIER"), shell=True, stdout=subprocess.PIPE)
	moderate2 = subprocess.Popen(cmd2 % (path, "MODERATE"), shell=True, stdout=subprocess.PIPE)
	high2 = subprocess.Popen(cmd2 % (path, "HIGH"), shell=True, stdout=subprocess.PIPE)
	low2 = subprocess.Popen(cmd2 % (path, "LOW"), shell=True, stdout=subprocess.PIPE)
	total2 = subprocess.Popen("""grep ^[^#] %s/0001.vcf | wc -l""" % path, shell=True, stdout=subprocess.PIPE)
	counts2 = [high2.communicate()[0].strip(), moderate2.communicate()[0].strip(), low2.communicate()[0].strip(), modifier2.communicate()[0].strip(), total2.communicate()[0].strip()]


	low_counts2 = defaultdict(int)
	high_counts2 = defaultdict(int)
	moderate_counts2 = defaultdict(int)
	modifier_counts2 = defaultdict(int)
	for each in low_effects:
		count_effect_cmd = """cat %s/0001.vcf| cut -f 8 | tr ";" "\n" | grep ^EFF= | cut -f 2 -d = | tr "," "\n" | grep %s | wc -l"""
		count_effect = subprocess.Popen(count_effect_cmd % (path, each), shell=True, stdout=subprocess.PIPE)
		count = count_effect.communicate()[0]
		low_counts2[each] = count.strip()
	for each in moderate_effects:
		count_effect_cmd = """cat %s/0001.vcf | cut -f 8 | tr ";" "\n" | grep ^EFF= | cut -f 2 -d = | tr "," "\n" | grep %s | wc -l"""
		count_effect = subprocess.Popen(count_effect_cmd % (path, each), shell=True, stdout=subprocess.PIPE)
		count = count_effect.communicate()[0]
		moderate_counts2[each] = count.strip()
	for each in modifier_effects:
		count_effect_cmd = """cat %s/0001.vcf | cut -f 8 | tr ";" "\n" | grep ^EFF= | cut -f 2 -d = | tr "," "\n" | grep %s | wc -l"""
		count_effect = subprocess.Popen(count_effect_cmd % (path, each), shell=True, stdout=subprocess.PIPE)
		count = count_effect.communicate()[0]
		modifier_counts2[each] = count.strip()
	for each in high_effects:
		count_effect_cmd = """cat %s/0001.vcf | cut -f 8 | tr ";" "\n" | grep ^EFF= | cut -f 2 -d = | tr "," "\n" | grep %s | wc -l"""
		count_effect = subprocess.Popen(count_effect_cmd % (path, each), shell=True, stdout=subprocess.PIPE)
		count = count_effect.communicate()[0]
		high_counts2[each] = count.strip()
	return render_to_response('snpdb/impact_snps.html', {"counts": counts,
	                                                     "counts2": counts2,
	                                                     "low_counts": dict(low_counts),
	                                                     "high_counts": dict(high_counts),
	                                                     "moderate_counts": dict(moderate_counts),
	                                                     "modifier_counts": dict(modifier_counts),
	                                                     "low_counts2": dict(low_counts2),
	                                                     "high_counts2": dict(high_counts2),
	                                                     "moderate_counts2": dict(moderate_counts2),
	                                                     "modifier_counts2": dict(modifier_counts2),
	                                                     "library1": library1,
	                                                     "library2": library2,
	                                                     "path": path}, context_instance=RequestContext(request))


#todo flag snps with multiple alternates
# Lists identified snps (those found to be unique for a library) by their impact type. Passed from difference_two_libraries
def impact_snps(request):
	path = request.POST.get('path')
	library1 = request.POST.get('lib1')
	library2 = request.POST.get('lib2')
	impact = request.POST.get('impact')

	cmd = """cat %s/0000.vcf | /usr/local/Cellar/snpeff/3.6c/share/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar filter "( EFF[*].IMPACT = '%s' )" | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar extractFields - POS REF ALT CHROM EFF[*].GENE EFF[*].EFFECT QUAL"""
	snps_effect = subprocess.Popen(cmd % (path, impact), shell=True, stdout=subprocess.PIPE)
	snps = []
	for line in snps_effect.stdout:
		if line:
			if '#POS' not in line:
				entry = line.split('\t')
				snps.append(entry)
	count = len(snps)
	paginator = Paginator(snps, 200)
	page = request.GET.get('page')

	# Calls utils method to append new filters or order_by to the current url
	filter_urls = build_orderby_urls(request.get_full_path(), ['library', 'snp_position', 'ref_base',
	                                                           'quality', 'alt_base',
	                                                           'chromosome__chromosome_name',
	                                                           'effect__effect_string'])
	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)

	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)
	c ={"path": path,
	    "results": results,
	    "library1": library1,
	    "library2": library2,
	    "filter_urls": filter_urls,
	    "toolbar_max": toolbar_max,
	    "toolbar_min": toolbar_min,
	    "count": count, }
	return render_to_response('snpdb/impact_snps_search.html', c, context_instance=RequestContext(request))


# Dumps a queryset into a csv file.
def dump(qs, outfile_path):
	writer = csv.writer(open(outfile_path, 'w'))
	keys = []
	values = []
	for obj in qs:
		for key, val in obj.items():
			values.append(val)
			if key not in keys:
				keys.append(key)
	value = [tuple(values[i:i+2]) for i in range(0, len(values), 2)]
	writer.writerow(keys)
	for each in value:
		writer.writerow(each)


# Reads a csv file and converts the data back into a dictionary.
def read(filename):
	impact_dict = {}
	for each in csv.reader(open(filename)):
		key = each[0]
		value = each[1]
		try:
			impact_dict[key] = int(value)
		except ValueError:
			impact_dict[key] = value
			pass
	return impact_dict


# unused code.
#----------------------------------------------------------------------------------------------------------------------------

# Commands to save the snpdb dashboard pie-charts. Should be run after each vcf import.
def save_snp_dashboard_files():
	high = Effect.objects.filter(effect_id=1, effect_string="HIGH").values("effect_class").annotate(Count('snp'))
	high_fields = high.keys()
	dump(high, '/Users/mcobb/Documents/djangoProjects/ngsdb03/snpdb/gcharts/high_impact.csv', high_fields)
	print "file saved"
	# high_count = defaultdict(int)
	# for i in high.iterator():
	# 	high_count[i] += 1
	# high_snp_total = sum(high_count.values())

	impact = Effect.objects.filter(effect_id=1).values("effect_string").annotate(Count('snp'))
	dump(impact, '/Users/mcobb/Documents/djangoProjects/ngsdb03/snpdb/gcharts/impact_impact.csv')
	print "file saved"
	# impact_count = defaultdict(int)
	# for i in impact.iterator():
	# 	impact_count[i] += 1
	# impact_snp_total = sum(impact_count.values())
	# print "impact_count"


	low = Effect.objects.filter(effect_id=1, effect_string="LOW").values("effect_class").annotate(Count('snp'))
	dump(low, '/Users/mcobb/Documents/djangoProjects/ngsdb03/snpdb/gcharts/low_impact.csv')
	print "file saved"
	# low_count = defaultdict(int)
	# for i in low.iterator():
	# 	low_count[i] += 1
	# print low_count
	# low_snp_total = sum(low_count.values())
	# print "low_count"

	moderate = Effect.objects.filter(effect_id=1, effect_string="MODERATE").values("effect_class").annotate(Count('snp'))
	dump(moderate, '/Users/mcobb/Documents/djangoProjects/ngsdb03/snpdb/gcharts/moderate_impact.csv')
	print "file saved"
	# moderate_count= defaultdict(int)
	# for i in moderate.iterator():
	# 	moderate_count[i] += 1
	# moderate_snp_total = sum(moderate_count.values())
	# print "moderate_count"

	modifier = Effect.objects.filter(effect_id=1, effect_string="MODIFIER").values("effect_class").annotate(Count('snp'))
	dump(modifier, '/Users/mcobb/Documents/djangoProjects/ngsdb03/snpdb/gcharts/modifier_impact.csv')
	print "file saved"
	# modifier_count = defaultdict(int)
	# for i in modifier.iterator():
	# 	modifier_count[i] += 1
	# modifier_snp_total = sum(modifier_count.values())
	# print "modifier_count"


""" Google Chart Images
	# lib_labels = []
	# lib_legend = []
	# org_labels = []
	# org_legend = []
	# impact_labels = []
	# high_labels = []
	# low_labels = []
	# moderate_labels = []
	# modifier_labels = []

	# for x in modifier_count.values():
	# 	percentage = float(x)/float(modifier_snp_total)*100
	# 	modifier_labels.append(round(percentage,2))
	# snps_by_modifier = Pie(modifier_labels).label(*modifier_labels).legend(*modifier_count.keys()).color("919dab", "D2E3F7",
	#                                                                                                      "658CB9", "88BBF7",
	#                                                                                                      "666E78").size(450,200)
	# snps_by_modifier.image().save('/Users/mcobb/Documents/djangoProjects/ngsdb03/snpdb/gcharts/snps_by_modifier_impact.png', 'png')


	# for x in moderate_count.values():
	# 	percentage = float(x)/float(moderate_snp_total)*100
	# 	moderate_labels.append(round(percentage,2))
	# snps_by_moderate = Pie(moderate_labels).label(*moderate_labels).legend(*moderate_count.keys()).color("919dab", "D2E3F7",
	#                                                                                                      "658CB9", "88BBF7",
	#                                                                                                      "666E78").size(550,200)
	# snps_by_moderate.image().save('/Users/mcobb/Documents/djangoProjects/ngsdb03/snpdb/gcharts/snps_by_moderate_impact.png', 'png')


	# for x in lib_snps:
	# 	percentage = float(x)/float(lib_snp_total)*100
	# 	lib_labels.append(round(percentage,2))
	# lib_legend.append(each['library__librarycode'])
	# snps_by_library = Pie([lib_labels]).label(*lib_labels).legend(*lib_legend).color("919dab", "D2E3F7",
	#                                                                                  "658CB9", "88BBF7",
	#                                                                                  "666E78").size(450,200)
	# snps_by_library.image()
	# snps_by_library.image().save('/Users/mcobb/Documents/djangoProjects/ngsdb03/snpdb/gcharts/snps_by_library.png', 'png')
	# print "saved snps_by_library"

	# for x in org_snps:
	# 	percentage = float(x)/float(org_snp_total)*100
	# 	org_labels.append(round(percentage,2))
	# org_legend.append(each['library__organism__organismcode'])
	# snps_by_organism = Pie(org_labels).label(*org_labels).legend(*org_legend).color("919dab", "D2E3F7",
	#                                                                                 "658CB9", "88BBF7",
	#                                                                                 "666E78").size(450,200)
	# snps_by_organism.image().save('/Users/mcobb/Documents/djangoProjects/ngsdb03/snpdb/gcharts/snps_by_organism.png', 'png')

	# for x in impact_count.values():
	# 	percentage = float(x)/float(low_snp_total)*100
	# 	low_labels.append(round(percentage,2))
	# snps_by_low = Pie(low_labels).label(*low_labels).legend(*impact_count.keys()).color("919dab", "D2E3F7",
	#                                                                                     "658CB9", "88BBF7",
	#                                                                                     "666E78").size(450,200)
	# snps_by_low.image().save('/Users/mcobb/Documents/djangoProjects/ngsdb03/snpdb/gcharts/snps_by_low_impact.png', 'png')

	# for x in impact_count.values():
	# 	percentage = float(x)/float(impact_snp_total)*100
	# 	impact_labels.append(round(percentage,2))
	# snps_by_impact = Pie(impact_labels).label(*impact_labels).legend(*impact_count.keys()).color("919dab", "D2E3F7",
	#                                                                                              "658CB9", "88BBF7",
	#                                                                                              "666E78").size(450,200)
	# snps_by_impact.image().save('/Users/mcobb/Documents/djangoProjects/ngsdb03/snpdb/gcharts/snps_by_impact.png', 'png')

	# for x in high_count.values():
	# 	percentage = float(x)/float(high_snp_total)*100
		# high_labels.append(round(percentage,2))
	# snps_by_high_impact = Pie(high_labels).label(*high_labels).legend(*high_count.keys()).color("919dab", "D2E3F7",
	#                                                                                             "658CB9", "88BBF7",
	#                                                                                             "666E78").size(450,200)
	# snps_by_high_impact.image().save('/Users/mcobb/Documents/djangoProjects/ngsdb03/snpdb/gcharts/snps_by_high_impact.png', 'png')"""

