from snpdb.models import *
from samples.models import *
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from utils import build_orderby_urls
from django.db.models import *
from django.template import RequestContext
from GChartWrapper import *
from collections import *
import subprocess
import datetime
import os
import csv
import vcf
import ast
from math import ceil
import PIL
from PIL import Image


# Returns the dashboard displaying summary charts of the loaded vcf files and libraries.
def dashboard(request):
	title = "SNP Dashboard"

	lib_count = SNP.objects.values("library__library_code").distinct().annotate(Count('snp_id'))
	lib_snps = []
	lib_snp_total = 0
	for each in lib_count.iterator():
		lib_snps.append(each['snp_id__count'])
		lib_snp_total += each['snp_id__count']

	org_count = SNP.objects.values("result__genome__organism__organismcode").distinct().annotate(Count('snp_id'))
	org_snps = []
	org_snp_total = 0
	for each in org_count.iterator():
		org_snps.append(each['snp_id__count'])
		org_snp_total += each['snp_id__count']

	path = os.path.abspath(os.path.dirname(__file__))
	chart_path = os.path.join(path, 'gcharts/%s_impact.csv')
	image_path = 'snpdb/static/snps_by_%s.png'
	images_path = 'snps_by_%s.png'
	if os.path.isfile(chart_path % 'high') and os.path.isfile(image_path % 'high'):
		print "file ", chart_path % 'high', "and file ", image_path % 'high', " was found."
		pass
	else:
		save_snp_dashboard_files(chart_path, image_path)
	totals = [lib_snp_total, org_snp_total]

	#read count files
	high_count = read(chart_path % 'high')
	low_count = read(chart_path % 'low')
	moderate_count = read(chart_path % 'moderate')
	modifier_count = read(chart_path % 'modifier')
	impact_count = read(chart_path % 'impact')


	images = [images_path % 'library', images_path % 'organism', images_path % 'impact', images_path % 'high',
	          images_path % 'low', images_path % 'moderate', images_path % 'modifier']

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
def snp_view(request):
	order_by = request.GET.get('order_by', 'snp_id')
	snp_list = SNP.objects.values('snp_id', 'snp_position', 'result', 'ref_base', 'alt_base',
	                              'heterozygosity', 'quality', 'library__library_code', 'chromosome__chromosome_name').order_by(order_by)
	count = len(snp_list)
	paginator = Paginator(snp_list, 50)
	page = request.GET.get('page')

	# Calls utils method to append new filters or order_by to the current url
	filter_urls = build_orderby_urls(request.get_full_path(), ['snp_id', 'snp_position', 'result',
	                                                           'ref_base', 'alt_base', 'heterozygosity',
	                                                           'quality', 'library__library_code', 'chromosome__chromosome_name'])
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


#Lists CNV values
def cnv(request):
	order_by = request.GET.get('order_by', 'cnv_id')
	cnv_list = CNV.objects.all().order_by(order_by)
	count = len(cnv_list)
	paginator = Paginator(cnv_list, 50)
	page = request.GET.get('page')

	# Calls utils method to append new filters or order_by to the current url
	filter_urls = build_orderby_urls(request.get_full_path(), ['cnv_id', 'chromosome__chromosome_name', 'coordinte',
	                                                           'CNV_value', 'result_id', 'library__library_code'])
	try:
		cnvs = paginator.page(page)
	except PageNotAnInteger:
		cnvs = paginator.page(1)
	except EmptyPage:
		cnvs = paginator.page(paginator.num_pages)

	toolbar_max = min(cnvs.number + 3, paginator.num_pages)
	toolbar_min = max(cnvs.number - 3, 0)

	return render_to_response('snpdb/CNV.html', {"cnvs": cnvs,
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
	filter_urls = build_orderby_urls(request.get_full_path(), ['stats_id', 'snp',
	                                                           'stats_cvterm', 'cv_value'])
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

	result_list = SNP.objects.values('snp_id', 'snp_position', 'result', 'ref_base', 'alt_base',
	                                 'heterozygosity', 'quality', 'library__library_code', 'chromosome__chromosome_name').filter(**filter_dict)

	order_by = request.GET.get('order_by', 'snp_id')
	result_list = result_list.order_by(order_by)
	filter_urls = build_orderby_urls(request.get_full_path(), ['snp_id', 'snp_position', 'result',
	                                                           'ref_base', 'alt_base', 'heterozygosity',
	                                                           'quality', 'library__library_code', 'chromosome__chromosome_name'])
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
	return render_to_response('snpdb/compare_gene_library.html', )


# Returns a list of libraries that the desired gene is found in.
def compare_gene_lib_filter(request):
	order_by = request.GET.get('order_by', 'library__library_code')
	gene = request.GET.get('s')
	genes = gene.split()

	genomes = Feature.objects.values_list('genome_id', flat=True).filter(geneid__in=genes).distinct()
	libraries = []
	for each in genomes:
		result_list = SNP.objects.values('library__library_code', 'result__genome__organism__organismcode', 'result__genome__version', 'result__genome__genome_id').filter(result__genome__genome_id=each).distinct().order_by(order_by)
		libraries.append(result_list)
	page = request.GET.get('page')
	filter_urls = build_orderby_urls(request.get_full_path(), ['library__library_code',
	                                                           'result__genome__organism__organismcode',
	                                                           'result__genome____genome_id', 'result__genome__version'])
	count = len(libraries[0])
	paginator = Paginator(libraries, 50)
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
	                                                                     "toolbar_min": toolbar_min})


# Returns the comparison of a gene across specific libraries.
def compare_gene_lib_filter_results_effect(request):
	# order_by = request.GET.get('order_by', 'library__library_code')
	gene_string = request.GET.get('s')
	genes = gene_string.split()
	library = request.GET.getlist('check')
	test = {}
	for gene in genes:
		try:
			cds_fmin = Feature.objects.values_list('fmin', flat=True).filter(geneid=gene, featuretype='CDS')[0]
			cds_fmax = Feature.objects.values_list('fmax', flat=True).filter(geneid=gene, featuretype='CDS')[0]
		except IndexError:
			cds_fmin = 0
			cds_fmax = 0

		try:
			fmin = Feature.objects.filter(geneid=gene).filter(featuretype='gene').values('fmin')[0]
			fmax = Feature.objects.filter(geneid=gene).filter(featuretype='gene').values('fmax')[0]
		except IndexError:
			fmin = 0
			fmax = 0

		chromosome = Feature.objects.filter(geneid=gene).filter(featuretype='gene').values_list('chromosome', flat=True)[0]

		result_list = SNP.objects.filter(effect__effect_id=6, effect__effect_string__exact=gene,
		                                 library__library_code__in=library).values('library', 'library__library_code', 'snp_id',
		                                                                           'snp_position', 'ref_base', 'alt_base',
		                                                                           'heterozygosity', 'quality',
		                                                                           'chromosome__chromosome_name', 'effect__effect_string',
		                                                                           'effect__effect_class', 'effect__effect').distinct().order_by('snp_position')
		#Checks to see if tuples have all libraries present. Inserts blank tuples if not.
		for each in result_list:
			new_tuple = [(None, None, None, gene, cds_fmin, cds_fmax, fmin['fmin'], fmax['fmax'], chromosome, each['snp_position'])] * len(library)
			curr_library = each['library__library_code']
			tup = (curr_library, each['ref_base'], each['alt_base'], gene, cds_fmin, cds_fmax, fmin['fmin'], fmax['fmax'], chromosome, each['snp_position'])
			index = library.index(curr_library)
			if each['snp_position'] in test:
				current_tup = test[each['snp_position']]
				current_tup[index] = tup
				test[each['snp_position']] = current_tup
			else:
				new_tuple[index] = tup
				test[each['snp_position']] = new_tuple
	test = OrderedDict(sorted(test.items(), key=lambda key: key[0]))
	count = len(test)
	filter_urls = build_orderby_urls(request.get_full_path(), ['gene', 'snp_position', 'ref_base', 'alt_base', 'library__library_code', 'fmin', 'fmax'])

	paginator = Paginator(test.items(), 50)
	page = request.GET.get('page')
	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)

	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)
	return render_to_response('snpdb/compare_gene_library_filter_result.html', {"results": results,
	                                                                            "genes": genes,
	                                                                            "gene": gene_string,
	                                                                            "library": library,
	                                                                            "test": test,
	                                                                            "count": count,
	                                                                            "library_group": sorted(library),
	                                                                            "filter_urls": filter_urls,
	                                                                            "toolbar_max": toolbar_max,
	                                                                            "toolbar_min": toolbar_min}, context_instance=RequestContext(request))


# Returns the list of genes found within the selected libraries.
# todo need to change so that it references effect table rather than feature table
def compare_gene_lib_filter_results(request):
	order_by = request.GET.get('order_by', 'library__library_code')
	gene = request.GET.get('s')
	library = request.GET.getlist('check')

	#Gets the start and stop position of the coding region of the gene.
	cds_fmin = Feature.objects.values_list('fmin', flat=True).filter(geneid=gene, featuretype='CDS')[0]
	cds_fmax = Feature.objects.values_list('fmax', flat=True).filter(geneid=gene, featuretype='CDS')[0]

	#Gets the start and stop position of gene.
	fmin = Feature.objects.filter(geneid=gene).filter(featuretype='gene').values('fmin')[0]
	fmax = Feature.objects.filter(geneid=gene).filter(featuretype='gene').values('fmax')[0]

	#Collects libraries that are effected by this gene
	result_list = SNP.objects.values('snp_id', 'snp_position',
	                                 'ref_base', 'alt_base',
	                                 'library__library_code').filter(library__library_code__in=library,
	                                                                 snp_position__range=(Feature.objects.values_list('fmin', flat=True).filter(geneid=gene).filter(featuretype='gene')[0],
	                                                                                      Feature.objects.values_list('fmax', flat=True).filter(geneid=gene).filter(featuretype='gene')[0]),
	                                                                 chromosome__chromosome_name=Feature.objects.values_list('chromosome', flat=True).filter(geneid=gene).filter(featuretype='gene')[0]).order_by(order_by)
	snp_group = []
	library_group = []
	max_snps = 0
	count = 0
	for each in result_list:
		snp_position = each['snp_position']
		library = each['library__library_code']
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
	filter_urls = build_orderby_urls(request.get_full_path(), ['snp_id', 'snp_position', 'ref_base', 'alt_base', 'library__library_code'])
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
	                                                           'alt_base', 'library__library_code'])
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


# Returns all snps found within the gene location regardless of library.
def gene_snps_filter(request):
	flanks = int(request.GET.get('f'))
	order_by = request.GET.get('order_by', 'library__library_code')
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
	result_list = SNP.objects.values('library__library_code', 'result_id',
	                                 'chromosome__chromosome_name', 'snp_id',
	                                 'snp_position', 'ref_base',
	                                 'alt_base').filter(snp_position__range=((Feature.objects.values_list('fmin', flat=True).filter(geneid=gene).filter(featuretype='gene')[0])+flanks,
	                                                                         (Feature.objects.values_list('fmax', flat=True).filter(geneid=gene).filter(featuretype='gene')[0])+flanks),
	                                                    chromosome__chromosome_name=Feature.objects.values_list('chromosome',
	                                                                                                            flat=True).filter(geneid=gene).filter(featuretype='gene')[0]).order_by(order_by)
	count = result_list.count()
	paginator = Paginator(result_list, 50)
	page = request.GET.get('page')
	filter_urls = build_orderby_urls(request.get_full_path(), ['library__library_code', 'result_id',
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
	lib_list = Library.objects.values('library_code').order_by('library_code')
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
	order_by = request.GET.get('order_by', 'library__library_code')
	gene = request.GET.get('s')
	library = request.GET.get('lib')
	cds_fmin = Feature.objects.values_list('fmin', flat=True).filter(geneid=gene, featuretype='CDS')[0]
	cds_fmax = Feature.objects.values_list('fmax', flat=True).filter(geneid=gene, featuretype='CDS')[0]
	fmin = Feature.objects.values_list('fmin', flat=True).filter(geneid=gene).filter(featuretype='gene')[0]
	fmax = Feature.objects.values_list('fmax', flat=True).filter(geneid=gene).filter(featuretype='gene')[0]
	result_list = SNP.objects.values('library__library_code', 'result_id',
	                                 'chromosome__chromosome_name', 'snp_id',
	                                 'snp_position', 'ref_base',
	                                 'alt_base', 'quality',
	                                 'heterozygosity').filter(snp_position__range=(Feature.objects.values_list('fmin', flat=True).filter(geneid=gene).filter(featuretype='gene')[0],
	                                                                               Feature.objects.values_list('fmax', flat=True).filter(geneid=gene).filter(featuretype='gene')[0]),
	                                                          library__library_code=library,
	                                                          chromosome__chromosome_name=Feature.objects.values_list('chromosome',
	                                                                                                                  flat=True).filter(geneid=gene).filter(featuretype='gene')[0]).order_by(order_by)
	count = result_list.count()
	page = request.GET.get('page')
	filter_urls = build_orderby_urls(request.get_full_path(), ['library__library_code', 'result_id',
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

	print toolbar_max
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
	results = SNP.objects.values('library_id',
	                             'library__library_code', 'result__genome__organism__organismcode',
	                             ).distinct().annotate(num_snps=Count('snp_id'),
	                                                   hetero=BooleanSum('heterozygosity'),
	                                                   indel=BooleanSum('snp_type__indel'),
	                                                   trans=BooleanSum('snp_type__transition'),
	                                                   ).order_by(order_by)
	result = []
	for each in results:
		library=each['library__library_code']
		organismcode = SNP.objects.values_list('result__genome__organism__organismcode', flat=True).filter(library__library_code=library)[0]
		contig = get_chromosome_size(organismcode)
		for key, value in contig.iteritems():
			each[key] = value
		result.append(each)
	paginator = Paginator(result, 50)
	page = request.GET.get('page')
	count = len(result)

	# Calls utils method to append new filters or order_by to the current url
	filter_urls = build_orderby_urls(request.get_full_path(), ['library__library_id', 'library__library_code', 'snp_id', 'num_snps', 'hetero', 'homo', 'indel', 'trans', 'snp_density'])
	try:
		result = paginator.page(page)
	except PageNotAnInteger:
		result = paginator.page(1)
	except EmptyPage:
		result = paginator.page(paginator.num_pages)

	toolbar_max = min(result.number + 4, paginator.num_pages)
	toolbar_min = max(result.number - 4, 0)

	return render_to_response('snpdb/library_snp_summary.html', {"result": result,
	                                                             "count": count,
	                                                             "filter_urls": filter_urls,
	                                                             "paginator": paginator,
	                                                             "toolbar_max": toolbar_max,
	                                                             "toolbar_min": toolbar_min})



def genes_from_effect(results, library, order_by):
	snp_dict = {}
	for each in results:
		current_genes = []
		if each['library__library_code'] == library:
			if not each['effect__effect'] or each['effect__effect'] == 6:
				print "worked"
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


#todo determine if snps are in coding region of gene.
# Returns snps found in a library and chromosome.
def library_chromosome_snps_filter(request):
	chromosome = request.GET.get('s')
	library = request.GET.get('lib')
	order_by = request.GET.get('order_by', 'snp_position')
	genome = SNP.objects.values_list('result__genome__genome_id', flat=True).filter(library__library_code=library).distinct()[0]

	#Collects the ranges of all genes for the specific chromosome
	ranges = Feature.objects.values_list('fmin', 'fmax', 'chromosome').filter(chromosome=chromosome).filter(featuretype='gene', genome_id=genome).order_by('fmin')
	# result_list = []
	for each in ranges:
		#Collects snps found within the gene range
		# results = SNP.objects.values('library__library_code', 'result_id',
		#                              'chromosome__chromosome_name',
		#                              'snp_position', 'ref_base', 'alt_base', 'quality',
		#                              'heterozygosity').filter(snp_position__range=(each[0],
		#                                                                            each[1]),
		#                                                       library__library_code=library,
		#                                                       chromosome__chromosome_name=each[2]).order_by(order_by)
		# if results is not None:
		# 	result_list.append(results)

		#Collects all genes found within the chromosome
		results = SNP.objects.values('library__library_code', 'result_id',
		                             'chromosome__chromosome_name',
		                             'snp_position', 'ref_base', 'alt_base', 'quality',
		                             'heterozygosity').filter(library__library_code=library,
		                                                      chromosome__chromosome_name=each[2]).order_by(order_by)

	count = len(results)
	page = request.GET.get('page')
	filter_urls = build_orderby_urls(request.get_full_path(), ['library__library_code', 'result_id',
	                                                           'chromosome__chromosome_name', 'snp_id',
	                                                           'snp_position', 'ref_base', 'alt_base',
	                                                           'quality', 'heterozygosity'])
	paginator = Paginator(results, 50)
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
	libraries = Library.objects.values('library_code').distinct().order_by('library_code')
	paginator = Paginator(libraries, 300)

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
	results = SNP.objects.values('chromosome__chromosome_name',
	                             'library_id', 'library__library_code',
	                             'result__genome__organism__organismcode').filter(library__library_code=library).annotate(num_snps=Count('snp_id'),
	                                                                                                                      hetero=BooleanSum('heterozygosity'),
	                                                                                                                      indel=BooleanSum('snp_type__indel'),
	                                                                                                                      trans=BooleanSum('snp_type__transition'))
	organismcode = SNP.objects.values_list('result__genome__organism__organismcode', flat=True).filter(library__library_code=library)[0]
	library_size = get_chromosome_size(organismcode)
	result_list = results.order_by(order_by)
	paginator = Paginator(result_list, 50)
	page = request.GET.get('page')

	# Calls utils method to append new filters or order_by to the current url
	filter_urls = build_orderby_urls(request.get_full_path(), ['chromosome__chromosome_name', 'library__librarysize', 'library_id', 'library__library_code',
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
	                                                                               "library_size": library_size,
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
	                                                                "toolbar_min": toolbar_min}, context_instance=RequestContext(request))


# todo change to access genes through the Effect table.
# Returns a full list of genes found within a specific library. Currently connects through the feature table.
def gene_list(request):
	order_by = request.GET.get('order_by', 'chromosome')
	library = request.GET.get('lib')
	results = Feature.objects.values('geneid', 'fmin', 'fmax', 'chromosome').filter(featuretype='gene',
	                                                                                genome__organism__library__library_code=library).order_by(order_by)
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


# Displays the search page to compare two groups of libraries for unique and similar snps.
def compare_two_libraries(request):
	ref_genome = request.GET.get('ref_genome')
	if ref_genome:
		lib_list = Library.objects.values('library_code', 'result__genome__organism__organismcode').filter(result__genome__organism__organismcode=ref_genome).distinct().order_by('library_code')
	else:
		lib_list = Organism.objects.values('organismcode').distinct().order_by('organismcode')
	page = request.GET.get('page')
	paginator = Paginator(lib_list, 500)

	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)
	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)
	return render_to_response('snpdb/compare_libraries.html', {"results": results,
	                                                           "ref_genome": ref_genome,
	                                                           "paginator": paginator,
	                                                           "toolbar_max": toolbar_max,
	                                                           "toolbar_min": toolbar_min}, context_instance=RequestContext(request))


#Compares multiple libraries by running vcf-contrast. Returns the results and counts the number of snps by impact types
def effects_by_vcf(request):
	library_1 = request.GET.getlist('check1')
	library_2 = request.GET.getlist('check2')
	wt = request.GET.get('wt')

	library_1.sort()
	library_2.sort()

	#Captures vcf file location
	vcf1 = VCF_Files.objects.values_list('vcf_path', flat=True).filter(library__library_code__in=library_1).distinct()
	vcf2 = VCF_Files.objects.values_list('vcf_path', flat=True).filter(library__library_code__in=library_2).distinct()

	#Gets path of vcf files.
	direct = os.path.abspath(os.path.dirname(__file__))
	pro_dir = re.findall('(^.*)\/snpdb', direct)[0]
	vcf_path = os.path.join(direct, 'vcf_files')

	#Collects all libraries to be compared.
	group_1_path = []
	for each in vcf1:
		vcf1_path = os.path.join(pro_dir, each)
		group_1_path.append(vcf1_path)
	group_1_path.sort()

	group_2_path = []
	for each in vcf2:
		vcf2_path = os.path.join(pro_dir, each)
		group_2_path.append(vcf2_path)
	group_2_path.sort()

	libraries = group_1_path + group_2_path
	libs = library_1 + library_2
	vcf_string = '_'.join(libs)

	#Determines the location of where analysis results will be stored.
	path = os.path.join(vcf_path, 'vcf_contrast_%s_%s' % (vcf_string, datetime.datetime.utcnow().strftime("%Y-%m-%d")))
	merge_file2 = os.path.join(path, 'merge_contrast.vcf')
	analysis_path = os.path.join('vcf_contrast_%s_%s' % (vcf_string, datetime.datetime.utcnow().strftime("%Y-%m-%d")), 'merge_contrast_replace.vcf')


	#Checks to see if analysis has already been completed. If the analysis files are not present, bcftools is called.
	if os.path.isdir(path):
		print "File already present"
		replace_file = os.path.join(path, 'merge_contrast_replace.vcf')
		pass
	else:
		os.mkdir(path)
		#Checks to see if files have been zipped and indexed. Bcftools requires indexed vcf files.
		for fname in libraries:
			if os.path.isfile(fname):
				# zips and indexes vcf-files for vcf-merge
				try:
					subprocess.check_call(['bgzip', fname])
					subprocess.check_call(['tabix', '-p', 'vcf', '%s.gz' % fname])
				except IOError:
					pass
			elif os.path.isfile('%s.gz' % fname):
				print "files already zipped"

		#Creates a string of all zipped file
		zip_vcf = ''
		for each in libraries:
			zips = str(each) + '.gz'
			zip_vcf = zip_vcf + ' ' + zips

		#Runs the vcf-merge command.
		merge_file = os.path.join(path, 'merge.vcf')

		p = subprocess.call(["""bcftools merge -m none --force-samples %s > %s""" % (zip_vcf, merge_file)], shell=True)
		# out, err = p.communicate()
		# print out, err
		print "files merged"

		# #collects all file ids.
		add_code = []
		neg_code = []

		for lib in library_1:
			add_code.append("s" + lib)

		for lib in library_2:
			neg_code.append("s" + lib)

		add1 = '+' + ','.join(add_code)
		neg1 = '-' + ','.join(neg_code)
		add2 = '+' + ','.join(neg_code)
		neg2 = '-' + ','.join(add_code)


		#zips replace file for vcf-contrast
		try:
			subprocess.check_call(['bgzip', merge_file])
			subprocess.check_call(['tabix', '-p', 'vcf', '%s.gz' % merge_file])
		except IOError:
			pass

		# print "calling vcf-contrast"
		zip_replace = merge_file + '.gz'
		vcf_contrast1 = os.path.join(path, 'vcf_contrast_1.vcf')
		vcf_contrast2 = os.path.join(path, 'vcf_contrast_2.vcf')

		subprocess.call(["""vcf-contrast -n %s %s %s > %s""" % (add1, neg1, zip_replace, vcf_contrast1)], shell=True)
		subprocess.call(["""vcf-contrast -n %s %s %s > %s""" % (add2, neg2, zip_replace, vcf_contrast2)], shell=True)

		#zips replace file for vcf-contrast
		try:
			subprocess.check_call(['bgzip', vcf_contrast1])
			subprocess.check_call(['tabix', '-p', 'vcf', '%s.gz' % vcf_contrast1])
			subprocess.check_call(['bgzip', vcf_contrast2])
			subprocess.check_call(['tabix', '-p', 'vcf', '%s.gz' % vcf_contrast2])
		except IOError:
			pass

		#merging vcf_contrast files
		print "Merging vcf_contrast iterations"
		p = subprocess.Popen(["""bcftools merge --force-samples -m none %s.gz %s.gz > %s""" % (vcf_contrast1, vcf_contrast2, merge_file2)], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
		out, err = p.communicate()
		print "files merged"

		# Replaces all missing genotypes with wildtype genotypes
		replace_file = os.path.join(path, 'merge_contrast_replace.vcf')
		p =subprocess.Popen(["""bcftools +missing2ref %s > %s """ % (merge_file2, replace_file)], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
		out, err = p.communicate()

	#Opens the returned vcf-contrast file and counts the data.
	print "opening vcf-contrast"
	lib_effect = []
	lib_total = 0

	vcf_reader = vcf.Reader(open('%s' % replace_file, 'r'))
	date = datetime.datetime.utcnow().strftime("%Y-%m-%d").replace('-', '')
	source = 'source_' + date + '.1'
	cmd = vcf_reader.metadata[source][0]

	group1 = re.findall('\+(.*) \-', cmd)[0].split(',')
	group2 = re.findall('\+.* \-(.*) ', cmd)[0].split(',')

	lib_high_effects = defaultdict(int)
	lib_moderate_effects = defaultdict(int)
	lib_modifier_effects = defaultdict(int)
	lib_low_effects = defaultdict(int)

	#Keeps track of the total library counts: [High, Moderate, Low, Modifier, Consistent, Total]
	lib_total_counts = [0, 0, 0, 0, 0, 0, '']

	# equivalent_gts = ['0/1', '1/1']
	for record in vcf_reader:

		group1_gt = []
		group2_gt = []
		group1_eq = False
		group2_eq = False
		if len(group1) > 1:

			for each in group1:
				if record.genotype(each)['GT']:
					if record.genotype(each)['GT'] == '0/0':
						group1_gt.append('WT')
					else:
						group1_gt.append('SNP')

				each2 = "2:%s" % each
				if record.genotype(each2)['GT']:
					if record.genotype(each2)['GT'] == '0/0':
						group1_gt.append('WT')
					else:
						group1_gt.append('SNP')

			group1_eq = check_equal(group1_gt)

		if len(group2) > 1:
			for each in group2:
				if record.genotype(each)['GT']:
					if record.genotype(each)['GT'] == '0/0':
						group2_gt.append('WT')
					else:
						group2_gt.append('SNP')

				each2 = "2:%s" % each

				if record.genotype(each2)['GT']:
					if record.genotype(each2)['GT'] == '0/0':
						group2_gt.append('WT')
					else:
						group2_gt.append('SNP')

			group2_eq = check_equal(group2_gt)

		#Keeps track of what effect type each snp has. [high, moderate, low, modifier]
		lib_impact_counts = [0, 0, 0, 0]

		#Places each type of impact into dictionary of the effect. SNPs with multiple impacts
		# will have all impacts accounted for in the impact total.
		# i.e, SNPs with Downstream and Upstream effects will results in an addition to both impact counts.
		effects = record.INFO['ANN']

		high_eq = 0
		moderate_eq = 0
		low_eq = 0
		modifier_eq = 0

		for x in effects:
			eff = x.split('|')
			if eff[2] == "HIGH":
				lib_impact_counts[0] += 1
				lib_high_effects[eff[1]] += 1
				if group1_eq or group2_eq:
					high_eq += 1
			elif eff[2] == "MODERATE":
				lib_impact_counts[1] += 1
				lib_moderate_effects[eff[1]] += 1
				if group1_eq or group2_eq:
					moderate_eq += 1
			elif eff[2] == "LOW":
				lib_impact_counts[2] += 1
				lib_low_effects[eff[1]] += 1
				if group1_eq or group2_eq:
					low_eq += 1
			elif eff[2] == "MODIFIER":
				lib_impact_counts[3] += 1
				lib_modifier_effects[eff[1]] += 1
				if group1_eq or group2_eq:
					modifier_eq += 1

		if high_eq > 0:
			lib_high_effects["Equivalent SNPs"] += 1
		if moderate_eq > 0:
			lib_moderate_effects["Equivalent SNPs"] += 1
		if low_eq > 0:
			lib_low_effects["Equivalent SNPs"] += 1
		if modifier_eq > 0:
			lib_modifier_effects["Equivalent SNPs"] += 1

		# Counts the number of snps effected by each impact type. Snp is only counted once for each impact
		#  i.e. if SNP has two modifying impacts, it is only counted once.
		if sum(lib_impact_counts) > 0:
			lib_total_counts[5] = group1
			lib_total_counts[4] += 1

		if lib_impact_counts[0] > 0:
			lib_total_counts[0] += 1
		if lib_impact_counts[1] > 0:
			lib_total_counts[1] += 1
		if lib_impact_counts[2] > 0:
			lib_total_counts[2] += 1
		if lib_impact_counts[3] > 0:
			lib_total_counts[3] += 1

	lib_tuple = (dict(lib_high_effects), dict(lib_moderate_effects), dict(lib_low_effects), dict(lib_modifier_effects), lib_total_counts)
	lib_effect.append(lib_tuple)
	lib_total += lib_total_counts[4]

	return render_to_response('snpdb/effects_by_vcf.html', {"library1": library_1,
	                                                        "library2": library_2,
	                                                        "wt": wt,
	                                                        "lib1_high_effects": dict(lib_high_effects),
	                                                        "lib1_moderate_effects": dict(lib_moderate_effects),
	                                                        "lib1_modifier_effects": dict(lib_modifier_effects),
	                                                        "lib1_low_effects": dict(lib_low_effects),
	                                                        "lib1_total_counts": lib_total_counts,
	                                                        "lib1_total": lib_total,
	                                                        "lib1_effect": lib_effect,
	                                                        "add_code": group1,
	                                                        "neg_code": group2,
	                                                        "analysis_path": analysis_path})


# Checks if values in list are equal. Used to find snp equivalence.
def check_equal(gt_list):
	# if len(gt_list) > 1:
	# 	print gt_list
	# 	print len(set(gt_list)) <= 1
	return len(set(gt_list)) <= 1


# Returns the snp that are found from effects_by_vcf. Opens the vcf-contrast file.
def impact_snps(request):
	analysis_path = request.GET.get('analysis_path')
	add = ast.literal_eval(request.GET.get('add'))
	neg = ast.literal_eval(request.GET.get('neg'))
	wt = request.GET.get('wt')
	libraries = add + neg
	impact = request.GET.get('impact')
	order_by = request.GET.get('order_by', 'chromosome')
	s = request.GET.get('s')
	att = request.GET.get('att')
	high_ct = request.GET.get('high_ct')
	moderate_ct = request.GET.get('moderate_ct')
	low_ct = request.GET.get('low_ct')
	consistent = request.GET.get('consistent')

	add.sort()
	neg.sort()

	direct = os.path.abspath(os.path.dirname(__file__))
	vcf_path = os.path.join(direct, 'vcf_files')
	path = os.path.join(vcf_path, analysis_path)
	analysis_folder = os.path.join(vcf_path, analysis_path.split('/')[0])
	output_path = os.path.join(analysis_folder, '%s_impact.vcf' % impact)

	#If output file has not been created
	if not os.path.isfile(output_path):

		#If no specific sort is required
		if not s:
			cmd = """cat %s | java -jar /usr/local/snpEff/SnpSift.jar filter "( ANN[*].IMPACT = '%s')" > %s """
			subprocess.call(cmd % (path, impact, output_path), shell=True, stdout=subprocess.PIPE)

		#Sorts results by specified value
		else:
			if att == "0":
				s = int(s)
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar filter "(ANN[*].IMPACT = '%s') & (POS = %d)" | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar extractFields - POS REF ALT CHROM ANN[*].GENE ANN[*].EFFECT QUAL ANN[*].AA"""
			elif att == "ref":
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar filter "(ANN[*].IMPACT = '%s') & (REF = '%s')" | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar extractFields - POS REF ALT CHROM ANN[*].GENE ANN[*].EFFECT QUAL ANN[*].AA"""
			elif att == "alt":
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar filter "(ANN[*].IMPACT = '%s') & (ALT = '%s')" | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar extractFields - POS REF ALT CHROM ANN[*].GENE ANN[*].EFFECT QUAL ANN[*].AA"""
			elif att == "quality":
				s = int(s)
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar filter "(ANN[*].IMPACT = '%s') & (QUAL = %d)" | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar extractFields - POS REF ALT CHROM ANN[*].GENE ANN[*].EFFECT QUAL ANN[*].AA"""
			elif att == "chromosome":
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar filter "(ANN[*].IMPACT = '%s') & (CHROM =~ '%s')" | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar extractFields - POS REF ALT CHROM ANN[*].GENE ANN[*].EFFECT QUAL ANN[*].AA"""
			elif att == "impact":
				s = s.replace(' ', '_').upper()
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar filter "(ANN[*].IMPACT = '%s') & (ANN[*].EFFECT = '%s')" | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar extractFields - POS REF ALT CHROM ANN[*].GENE ANN[*].EFFECT QUAL ANN[*].AA"""
			elif att == "gene":
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar filter "(ANN[*].IMPACT = '%s') & (ANN[*].GENE = '%s')" | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar extractFields - POS REF ALT CHROM ANN[*].GENE ANN[*].EFFECT QUAL ANN[*].AA"""
			subprocess.Popen(cmd % (path, impact, s), shell=True, stdout=subprocess.PIPE)

	snp_dict = defaultdict(dict)
	vcf_reader = vcf.Reader(open(output_path, 'r'))

	for record in vcf_reader:
		snp = defaultdict(list)
		neg_eq = False
		add_eq = False
		pos = record.POS
		qual = record.QUAL
		chrom = record.CHROM
		effects = record.INFO['ANN']
		alt = ','.join(str(i) for i in record.ALT)
		ref = record.REF
		genes = []

		lib_dict = {}
		for lib in libraries:
			lib_dict[lib] = {'ref': ['No SNP'], 'alt': ['No SNP'], 'effect': ['No Effect']}

		for x in effects:
			data = x.split('|')
			eff = data[1]
			imp = data[2]

			if impact == imp:
				gene = data[3]

				if gene not in genes:
					genes.append(gene)
				# aa_change = effs[7]

				try:
					product = Feature.objects.values_list('geneproduct', flat=True).filter(geneid=gene, featuretype='gene')[0]
				except IndexError:
					product = gene

				try:
					wt_allele = SNP.objects.filter(chromosome__chromosome_name__startswith=chrom,
					                               snp_position=pos, library__library_code=wt).values_list('alt_base', flat=True)[0]
				except IndexError:
					wt_allele = "No SNP"

				try:
					fmin = Feature.objects.values_list('fmin', flat=True).filter(geneid=gene, featuretype='CDS')[0]
					fmax = Feature.objects.values_list('fmax', flat=True).filter(geneid=gene, featuretype='CDS')[0]
				except IndexError:

					try:
						fmin = Feature.objects.filter(geneid=gene).filter(featuretype='gene').values_list('fmin', flat=True)[0]
						fmax = Feature.objects.filter(geneid=gene).filter(featuretype='gene').values_list('fmax', flat=True)[0]
					except IndexError:
						fmin = 0
						fmax = 0

				if eff not in snp['effect']:
					snp['effect'].append(eff)

				bp_from_start = pos - fmin
				aa_from_start = int(ceil(bp_from_start/3))
				gene_length = int(ceil((fmax-fmin)/3))

				#Adds all alternate and references alleles
				for lib in libraries:
					alt_lib = "2:" + lib
					gt = record.genotype(lib)['GT']
					gt2 = record.genotype(alt_lib)['GT']

					if not gt.endswith('/0'):
						if pos == 125228:
							print lib, gt, gt2

						if 'No SNP' in lib_dict[lib]['ref'] and 'No SNP' in lib_dict[lib]['alt']:
							lib_dict[lib]['ref'] = [ref]
							lib_dict[lib]['alt'] = [alt]
							lib_dict[lib]['effect'] = [eff]

						elif alt not in lib_dict[lib]['alt']:
							lib_dict[lib]['alt'].append(alt)
							lib_dict[lib]['ref'].append(ref)

							lib_dict[lib]['alt'].sort()
							lib_dict[lib]['ref'].sort()

					else:
						if 'No SNP' in lib_dict[lib]['ref'] and 'No SNP' in lib_dict[lib]['alt']:
							lib_dict[lib]['ref'] = [ref]
							lib_dict[lib]['alt'] = ["WT"]
							lib_dict[lib]['effect'] = [eff]
						else:
							if 'WT' not in lib_dict[lib]['alt']:
								lib_dict[lib]['alt'].append('WT')

					if not gt2.endswith('/0'):
						if 'No SNP' in lib_dict[lib]['ref']:
							lib_dict[lib]['ref'] = [ref]

						if 'No SNP' in lib_dict[lib]['alt']:
							lib_dict[lib]['alt'] = [alt]
							lib_dict[lib]['effect'] = [eff]

						elif alt not in lib_dict[lib]['alt']:
							lib_dict[lib]['alt'].append(alt)
							lib_dict[lib]['ref'].append(ref)

							lib_dict[lib]['alt'].sort()
							lib_dict[lib]['ref'].sort()

					else:
						if 'No SNP' in lib_dict[lib]['alt']:
							lib_dict[lib]['ref'] = [ref]
							lib_dict[lib]['alt'] = ["WT"]
							lib_dict[lib]['effect'] = [eff]
						else:
							if 'WT' not in lib_dict[lib]['alt']:
								lib_dict[lib]['alt'].append('WT')

		#Collects whether the libraries are consistent in snps
		if len(add) > 1:
			add_gt = []
			for each in add:
				each2 = "2:%s" % each

				gt = record.genotype(each)['GT']
				gt2 = record.genotype(each2)['GT']

				if gt.endswith('/0'):
					add_gt.append('WT')
				else:
					add_gt.append('SNP')

				if gt2.endswith('/0'):
					add_gt.append('WT')
				else:
					add_gt.append('SNP')

			add_eq = check_equal(add_gt)

		if len(neg) > 1:
			neg_gt = []

			for each in neg:
				each2 = "2:%s" % each
				gt = record.genotype(each)['GT']
				gt2 = record.genotype(each2)['GT']

				if pos == 125228:
					print each, gt, gt2

				if gt.endswith('/0'):
					# print gt
					neg_gt.append('WT')
				else:
					# print gt
					neg_gt.append('SNP')

				if gt2.endswith('/0'):
					# print gt
					neg_gt.append('WT')
				else:
					# print gt
					neg_gt.append('SNP')

			if pos == 389093:
				print neg_gt
				print check_equal(neg_gt)
			neg_eq = check_equal(neg_gt)

		if not neg_eq:
			snp['group2_consistency'] = "False"
		else:
			snp['group2_consistency'] = "True"

		if not add_eq:
			snp['group1_consistency'] = "False"
		else:
			snp['group1_consistency'] = "True"

		if pos not in snp_dict:
			snp['chromosome'] = chrom
			snp['ref'] = [ref]
			snp['alt'] = [alt]
			snp['quality'] = [qual]
			snp['impact'] = [impact]
			snp['gene'] = genes
			snp['wt_allele'] = [wt_allele]
			snp['library_alleles'] = dict(lib_dict)
			snp['product'] = product
			snp['aa_from_start'] = [aa_from_start]
			snp['start'] = fmin
			snp['stop'] = fmax
			snp['gene_length'] = [gene_length]

			if consistent == "on":
				if snp['group1_consistency'] == "True" or snp['group2_consistency'] == "True":
					snp_dict[pos] = dict(snp)
				else:
					pass
			else:
				snp_dict[pos] = dict(snp)
		else:
			if qual not in snp_dict[pos]['quality']:
				snp_dict[pos]['quality'].append(qual)

			if gene not in snp_dict[pos]['gene']:
				snp_dict[pos]['gene'].append(genes)

			if impact not in snp_dict[pos]['impact']:
				snp_dict[pos]['impact'].append(impact)

			if eff not in snp_dict[pos]['effect']:
				snp_dict[pos]['effect'].append(eff)

			if wt_allele not in snp_dict[pos]['wt_allele']:
				snp_dict[pos]['wt_allele'].append(wt_allele)

			if product not in snp_dict[pos]['product']:
				snp_dict[pos]['product'].append(product)

			if aa_from_start not in snp_dict[pos]['aa_from_start']:
				snp_dict[pos]['aa_from_start'].append(aa_from_start)

			if gene_length not in snp_dict[pos]['gene_length']:
				snp_dict[pos]['gene_length'].append(gene_length)

			if alt not in snp_dict[pos]['alt']:

				for lib in libraries:
					alt_lib = "2:" + lib

					if record.genotype(lib)['GT'] == '0/1' or record.genotype(lib)['GT'] == '1/1':

						if 'No SNP' in snp_dict[pos]['library_alleles'][lib]['ref'] or 'No SNP' in snp_dict[pos]['library_alleles'][lib]['alt']:
							snp_dict[pos]['library_alleles'][lib]['ref'] = [ref]
							snp_dict[pos]['library_alleles'][lib]['alt'] = [alt]
							snp_dict[pos]['library_alleles'][lib]['effect'] = [eff]
						elif alt not in snp_dict[pos]['library_alleles'][lib]['alt']:
							snp_dict[pos]['library_alleles'][lib]['alt'].append(alt)
							snp_dict[pos]['library_alleles'][lib]['alt'].sort()

					if record.genotype(alt_lib)['GT'] == '0/1' or record.genotype(alt_lib)['GT'] == '1/1':

						if 'No SNP' in snp_dict[pos]['library_alleles'][lib]['ref'] or 'No SNP' in snp_dict[pos]['library_alleles'][lib]['alt']:
							snp_dict[pos]['library_alleles'][lib]['ref'] = [ref]
							snp_dict[pos]['library_alleles'][lib]['alt'] = [alt]
							snp_dict[pos]['library_alleles'][lib]['effect'] = [eff]
						elif alt not in snp_dict[pos]['library_alleles'][lib]['alt']:
							snp_dict[pos]['library_alleles'][lib]['alt'].append(alt)
							snp_dict[pos]['library_alleles'][lib]['alt'].sort()
							snp_dict[pos]['library_alleles'][lib]['ref'].sort()

			if ref not in snp_dict[pos]['ref']:
				if 'No SNP' in snp_dict[pos]['ref']:
					snp_dict[pos]['ref'] = [ref]
				else:
					snp_dict[pos]['ref'].append(ref)
					snp_dict[pos]['ref'].sort()

	test_dict = dict(snp_dict)
	if order_by == '0':
		sorted_snp = sorted(test_dict.iteritems())

	elif order_by == 'quality':
		sorted_snp = sorted(test_dict.iteritems(), key=lambda (k, v): v[order_by], reverse=True)

	else:
		sorted_snp = sorted(test_dict.iteritems(), key=lambda (k, v): v[order_by])

	count = len(snp_dict)
	paginator = Paginator(sorted_snp, 200)
	page = request.GET.get('page')

	# Calls utils method to append new filters or order_by to the current url
	filter_urls = build_orderby_urls(request.get_full_path(), ['chromosome', 'ref', 'quality', 'impact', 'gene',
	                                                           'gene_length', 'aa', 'wt_allele', 'alt', 'group1_consistency', 'group2_consistency'])
	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)

	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)
	c = {"analysis_path": analysis_path,
	     "paginator": paginator,
	     "results": results,
	     "libraries": libraries,
	     "add": add,
	     "impact": impact,
	     "neg": neg,
	     "wt": wt,
	     "high_ct": high_ct,
	     "low_ct": low_ct,
	     "moderate_ct":moderate_ct,
	     "filter_urls": filter_urls,
	     "toolbar_max": toolbar_max,
	     "toolbar_min": toolbar_min,
	     "count": count}
	return render_to_response('snpdb/impact_snps_search.html', c, context_instance=RequestContext(request))


#Displays a more in depth view of high and moderate impacts on a specific gene.
def gene_snp_summary(request):
	gene_id = request.GET.get('geneid')
	analysis_path = request.GET.get('analysis_path')
	gene_length = ast.literal_eval(request.GET.get('length'))[0]
	wt = request.GET.get('wt')

	direct = os.path.abspath(os.path.dirname(__file__))
	vcf_path = os.path.join(direct, 'vcf_files')
	path = os.path.join(vcf_path, analysis_path)

	eff = Feature.objects.filter(featuretype='gene', geneid=gene_id).values('geneproduct')
	try:
		effs = str(eff[0]['geneproduct'])
	except IndexError:
		effs = "No Gene"

	cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar filter "( EFF[*].GENE = '%s') & ((EFF[*].IMPACT = 'HIGH') | (EFF[*].IMPACT = 'MODERATE'))" | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar extractFields - POS REF ALT CHROM EFF[*].GENE EFF[*].EFFECT QUAL EFF[*].AA EFF[*].IMPACT"""
	cmd2 = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar filter "( EFF[*].GENE = '%s') & (EFF[*].IMPACT = 'LOW')" | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar extractFields - POS REF ALT CHROM EFF[*].GENE EFF[*].EFFECT QUAL EFF[*].AA EFF[*].IMPACT"""
	snps = subprocess.Popen(cmd % (path, gene_id), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	low_snps = subprocess.Popen(cmd2 % (path, gene_id), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	snp_list = []
	high_ct = 0
	moderate_ct = 0
	low_ct = 0

	for line in snps.stdout:

		snp_info = {}
		if line.startswith('#POS'):
			continue
		else:
			snp = line.split('\t')
			chrom = snp[3].split('_')[0]
			ref = snp[1]
			alt = snp[2]
			gene = snp[4]
			effect_type = snp[5]
			quality = snp[6]
			impact = snp[8]
			aa_change = snp[7]

			aa_pos = re.findall("(\d+)", aa_change)[0]

			if len(ref) > len(alt):
				gain_of_function = "True"
			else:
				gain_of_function = "False"


			snp_info['position'] = snp[0]
			snp_info['ref'] = ref
			snp_info['alt'] = alt
			snp_info['chromosome'] = chrom
			snp_info['gain_of_function'] = gain_of_function
			snp_info['gene'] = gene
			snp_info['impact'] = impact
			snp_info['quality'] = quality
			snp_info['effect'] = effect_type
			snp_info['aa_pos'] = aa_pos
			snp_info['percent_impacted'] = float( (gene_length - float(aa_pos)) / gene_length) * 100

			snp_list.append(snp_info)


			if snp[8].strip() == "HIGH":
				high_ct += 1
			elif snp[8].strip() == "MODERATE":
				moderate_ct += 1

	for line in low_snps.stdout:

		if line.startswith('#POS'):
			pass
		else:
			low_ct += 1

	return render_to_response('snpdb/gene_snp_summary.html', {"gene_id": gene_id,
	                                                          "wt": wt,
	                                                          "gene_name": effs,
	                                                          "high_ct": high_ct,
	                                                          "moderate_ct": moderate_ct,
	                                                          "low_ct": low_ct,
	                                                          "snp_list": snp_list,
	                                                          }, context_instance=RequestContext(request))


def get_chromosome_size(organismcode):
	genome_size = Chromosome.objects.filter(genome_name_id=organismcode).aggregate(genome_size=Sum('size'))
	return genome_size


# Asks the user for what library they would like to query.
def chrom_region(request):
	ref_genome = request.GET.get('ref_genome')
	if ref_genome:
		lib_list = Library.objects.values('library_code', 'result__genome__organism__organismcode').filter(result__genome__organism__organismcode=ref_genome).distinct().order_by('library_code')
	else:
		lib_list = Organism.objects.values('organismcode').distinct().order_by('organismcode')
	page = request.GET.get('page')
	paginator = Paginator(lib_list, 500)

	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)
	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)
	return render_to_response('snpdb/chrom_region.html', {"results": results,
	                                                      'ref_genome': ref_genome,
	                                                      "paginator": paginator,
	                                                      "toolbar_max": toolbar_max,
	                                                      "toolbar_min": toolbar_min}, context_instance=RequestContext(request))


# Asks the user what chromosome and region(bp) the user would like to query for SNPs
def chrom_region_search(request):
	library = request.GET.get('library')
	chromosome = SNP.objects.values_list('chromosome__chromosome_name').filter(library__library_code=library).distinct().order_by('chromosome__chromosome_name')
	return render_to_response('snpdb/chrom_region.html', {"chromosome": chromosome,
	                                                      "library": library,
	                                                      })


# Returns SNPs found within the specified chromosome and region.
def chrom_region_filter(request):
	library = request.GET.get('library')
	start = request.GET.get('from')
	stop = request.GET.get('to')
	chrom = request.GET.get('chrom')
	title = "SNP Region Summary"

	genes = SNP.objects.filter(effect__effect_id=6).values('snp_position', 'effect__effect_string',
	                                                       'effect__effect_group').filter(chromosome__chromosome_name=chrom, library__library_code=library,
	                                                                                      snp_position__range=(start, stop)).distinct()
	results = defaultdict(int)
	for each in genes:
		effect_group = each['effect__effect_group']
		impact = SNP.objects.filter(effect__effect_id=1,
		                            effect__effect_group=effect_group,).values('snp_position', 'ref_base', 'alt_base', 'heterozygosity',
		                                                                       'quality', 'effect__effect_string', 'effect__effect_class').filter(
			snp_position=each['snp_position'],
			chromosome__chromosome_name=chrom,
			library__library_code=library,).distinct()
		for x in impact:
			x['gene'] = each['effect__effect_string']
			if each['snp_position'] in results:
				results[each['snp_position']].append(x)
			else:
				results[each['snp_position']] = [x,]

	page = request.GET.get('page')
	paginator = Paginator(results.items(), 50)

	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)
	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)
	print toolbar_min, toolbar_max
	return render_to_response('snpdb/chrom_region_filter.html', {"chromosome": chrom,
	                                                             "library": library,
	                                                             "title": title,
	                                                             "results": results,
	                                                             "toolbar_max": toolbar_max,
	                                                             "toolbar_min": toolbar_min}, context_instance=RequestContext(request))


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
		for x in each:
			x = x.split(',')
			key = x[0].replace('(', '').replace("'", '')
			value = x[1].strip(')').replace("'", '')
			try:
				impact_dict[key] = int(value)
			except ValueError:
				impact_dict[key] = value
				pass
	return impact_dict


# Resizes the flowchart of the snp process. 
def snpdb_flowchart(request):

	image = os.path.join(os.path.abspath(settings.MEDIA_URL), 'protocols/snp_flowchart.png')
	resize_image = os.path.join(os.path.abspath(settings.MEDIA_URL), 'protocols/snp_flowchart_resize.png')
	basewidth = 800
	img = Image.open(image)
	wpercent = (basewidth / float(img.size[0]))
	hsize = int((float(img.size[1]) * float(wpercent)))
	img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
	img.save(resize_image)
	image_path = '/media/protocols/snp_flowchart_resize.png'
	return render_to_response('snpdb/snp_detection_process.html', {"image_path": image_path},
		                      context_instance=RequestContext(request))


# Commands to save the snpdb dashboard pie-charts. Should be run after each vcf import.
def save_snp_dashboard_files(chart_path, image_path):
	# Google Chart Images
	lib_labels = []
	lib_legend = []
	org_labels = []
	org_legend = []
	impact_labels = []
	high_labels = []
	low_labels = []
	moderate_labels = []
	modifier_labels = []
	high_keys = []
	low_keys = []
	moderate_keys = []
	modifier_keys = []
	impact_keys = []
	high_values = []
	low_values = []
	moderate_values = []
	modifier_values = []
	impact_values = []

	high = Effect.objects.filter(effect_id=1, effect_string="HIGH").values("effect_class").annotate(Count('snp'))
	dump(high, chart_path % 'high')
	for obj in high.iterator():
		for key, val in obj.items():
			high_values.append(val)
			if val not in high_keys and not isinstance(val, int):
				high_keys.append(val)
	high_value = [tuple(high_values[i:i+2]) for i in range(0, len(high_values), 2)]
	high_snp_total = sum(i[1] for i in high_value)
	for x in high_value:
		percentage = float(x[1])/float(high_snp_total)*100
		high_labels.append(round(percentage, 2))
	snps_by_high_impact = Pie(high_labels).label(*high_labels).legend(*high_keys).color("919dab", "D2E3F7",
	                                                                                    "658CB9", "88BBF7",
	                                                                                    "666E78").size(450, 200)
	snps_by_high_impact.image().save(image_path % 'high', 'png')
	print "high files saved"

	impact = Effect.objects.filter(effect_id=1).values("effect_string").annotate(Count('snp'))
	dump(impact, chart_path % 'impact')
	for obj in impact.iterator():
		for key, val in obj.items():
			print key, val
			impact_values.append(val)
			if val not in impact_keys and not isinstance(val, int):
				impact_keys.append(val)
	impact_value = [tuple(impact_values[i:i+2]) for i in range(0, len(impact_values), 2)]
	impact_snp_total = sum(i[1] for i in impact_value)
	for x in impact_value:
		percentage = float(x[1])/float(impact_snp_total)*100
		impact_labels.append(round(percentage,2))
	snps_by_impact = Pie(impact_labels).label(*impact_labels).legend(*impact_keys).color("919dab", "D2E3F7",
	                                                                                     "658CB9", "88BBF7",
	                                                                                     "666E78").size(450, 200)
	snps_by_impact.image().save(image_path % 'impact', 'png')
	print "impact files saved"

	low = Effect.objects.filter(effect_id=1, effect_string="LOW").values("effect_class").annotate(Count('snp'))
	dump(low, chart_path % 'low')
	for obj in low.iterator():
		for key, val in obj.items():
			low_values.append(val)
			if val not in low_keys and not isinstance(val, int):
				low_keys.append(val)
	low_value = [tuple(low_values[i:i+2]) for i in range(0, len(low_values), 2)]
	low_snp_total = sum(i[1] for i in low_value)
	for x in low_value:
		percentage = float(x[1])/float(low_snp_total)*100
		low_labels.append(round(percentage, 2))
	snps_by_low = Pie(low_labels).label(*low_labels).legend(*low_keys).color("919dab", "D2E3F7",
	                                                                         "658CB9", "88BBF7",
	                                                                         "666E78").size(450, 200)
	snps_by_low.image().save(image_path % 'low', 'png')
	print "low files saved"

	moderate = Effect.objects.filter(effect_id=1, effect_string="MODERATE").values("effect_class").annotate(Count('snp'))
	dump(moderate, chart_path % 'moderate')
	for obj in moderate.iterator():
		for key, val in obj.items():
			moderate_values.append(val)
			if val not in moderate_keys and not isinstance(val, int):
				moderate_keys.append(val)
	moderate_value = [tuple(moderate_values[i:i+2]) for i in range(0, len(moderate_values), 2)]
	moderate_snp_total = sum(i[1] for i in moderate_value)
	for x in moderate_value:
		percentage = float(x[1])/float(moderate_snp_total)*100
		moderate_labels.append(round(percentage, 2))
	snps_by_moderate = Pie(moderate_labels).label(*moderate_labels).legend(*moderate_keys).color("919dab", "D2E3F7",
	                                                                                             "658CB9", "88BBF7",
	                                                                                             "666E78").size(550, 200)
	snps_by_moderate.image().save(image_path % 'moderate', 'png')
	print "moderate files saved"

	modifier = Effect.objects.filter(effect_id=1, effect_string="MODIFIER").values("effect_class").annotate(Count('snp'))
	dump(modifier, chart_path % 'modifier')
	for obj in modifier.iterator():
		for key, val in obj.items():
			modifier_values.append(val)
			if val not in modifier_keys and not isinstance(val, int):
				modifier_keys.append(val)
	modifier_value = [tuple(modifier_values[i:i+2]) for i in range(0, len(modifier_values), 2)]
	modifier_snp_total = sum(i[1] for i in modifier_value)
	for x in modifier_value:
		percentage = float(x[1])/float(modifier_snp_total)*100
		modifier_labels.append(round(percentage, 2))
	snps_by_modifier = Pie(modifier_labels).label(*modifier_labels).legend(*modifier_keys).color("919dab", "D2E3F7",
	                                                                                             "658CB9", "88BBF7",
	                                                                                             "666E78").size(450, 200)
	snps_by_modifier.image().save(image_path % 'modifier', 'png')
	print "modifier files saved"

	lib_count = SNP.objects.values("library__library_code").distinct().annotate(Count('snp_id'))
	lib_snps = []
	lib_snp_total = 0
	for each in lib_count.iterator():
		lib_snps.append(each['snp_id__count'])
		lib_snp_total += each['snp_id__count']
	for x in lib_snps:
		percentage = float(x)/float(lib_snp_total)*100
		lib_labels.append(round(percentage, 2))
	lib_legend.append(each['library__library_code'])
	snps_by_library = Pie([lib_labels]).label(*lib_labels).legend(*lib_legend).color("919dab", "D2E3F7",
	                                                                                 "658CB9", "88BBF7",
	                                                                                 "666E78").size(450, 200)
	snps_by_library.image()
	snps_by_library.image().save(image_path % 'library', 'png')
	print "saved snps_by_library"

	org_count = SNP.objects.values("library__organism__organismcode").distinct().annotate(Count('snp_id'))
	org_snps = []
	org_snp_total = 0
	for each in org_count.iterator():
		org_snps.append(each['snp_id__count'])
		org_snp_total += each['snp_id__count']
	for x in org_snps:
		percentage = float(x)/float(org_snp_total)*100
		org_labels.append(round(percentage, 2))
	org_legend.append(each['library__organism__organismcode'])
	snps_by_organism = Pie(org_labels).label(*org_labels).legend(*org_legend).color("919dab", "D2E3F7",
	                                                                                "658CB9", "88BBF7",
	                                                                                "666E78").size(450, 200)
	snps_by_organism.image().save(image_path % 'organism', 'png')
	print "saved snps_by_organism"


# Unused Code
#-----------------------------------------------------------------------------------------------
# # Returns all snps found within a library using the effect table.
# def library_snps(request):
# 	order_by = request.GET.get('order_by', 'snp_id').encode("ascii")
# 	library = request.GET.get('lib')
# 	count = request.GET.get('count')
# 	selection = request.GET.get('att')
# 	filter_on = request.GET.get('s')
# 	filter_dict = {}
# 	if selection:
# 		filter_dict[str(selection)] = str(filter_on)
# 	if filter_dict:
# 		if selection == 'effect__effect_string':
# 			results = SNP.objects.filter(effect__effect_id=6, effect__effect_string__exact=filter_on.decode('utf-8'),
# 			                             effect__effect_class__endswith='SYNONYMOUS_CODING'.decode('utf-8'),
# 			                             library__library_code=library).values('library', 'library__library_code', 'snp_id',
# 			                                                                   'snp_position', 'ref_base', 'alt_base',
# 			                                                                   'heterozygosity', 'quality',
# 			                                                                   'chromosome__chromosome_name', 'effect__effect_string',
# 			                                                                   'effect__effect_class', 'effect__effect')
# 		else:
# 			results = SNP.objects.filter(**filter_dict).filter(library__library_code=library).values('library', 'library__library_code', 'snp_id',
# 			                                                                                         'snp_position', 'ref_base', 'alt_base',
# 			                                                                                         'heterozygosity', 'quality',
# 			                                                                                         'chromosome__chromosome_name', 'effect__effect_string',
# 			                                                                                         'effect__effect_class', 'effect__effect')
# 	else:
# 		results = SNP.objects.values('library', 'library__library_code', 'snp_id',
# 		                             'snp_position', 'ref_base', 'alt_base',
# 		                             'heterozygosity', 'quality',
# 		                             'chromosome__chromosome_name', 'effect__effect_string',
# 		                             'effect__effect_class', 'effect__effect')
#
# 	sorted_snp_dict = genes_from_effect(results, library, order_by)
# 	paginator = Paginator(sorted_snp_dict, 100)
# 	page = request.GET.get('page')
#
# 	# Calls utils method to append new filters or order_by to the current url
# 	filter_urls = build_orderby_urls(request.get_full_path(), ['library', 'library__library_code', 'snp_id',
# 	                                                           'snp_position', 'ref_base', 'alt_base',
# 	                                                           'heterozygosity', 'quality',
# 	                                                           'chromosome__chromosome_name',
# 	                                                           'effect__effect_string'])
# 	try:
# 		results = paginator.page(page)
# 	except PageNotAnInteger:
# 		results = paginator.page(1)
# 	except EmptyPage:
# 		results = paginator.page(paginator.num_pages)
#
# 	toolbar_max = min(results.number + 4, paginator.num_pages)
# 	toolbar_min = max(results.number - 4, 0)
#
# 	return render_to_response('snpdb/library_snps.html', {"results": results,
# 	                                                      "library": library,
# 	                                                      "order_by": order_by,
# 	                                                      "filter_urls": filter_urls,
# 	                                                      "paginator": paginator,
# 	                                                      "toolbar_max": toolbar_max,
# 	                                                      "toolbar_min": toolbar_min,
# 	                                                      "count": count})
