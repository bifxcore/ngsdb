from snpdb.models import *
from samples.models import *
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext
from django.db.models import *
from django_boolean_sum import BooleanSum
from django.db import connection

from utils import build_orderby_urls
from GChartWrapper import *
from collections import *
import os
import csv
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

#============================================================================#
# SNP Query Views
#============================================================================#

# Returns a list of libraries that the desired gene is found in.
def compare_gene_lib(request):
	order_by = request.GET.get('order_by', 'library__library_code')
	gene = request.GET.get('s')

	if not gene:
		return render_to_response('snpdb/compare_gene_library.html')

	else:
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
		count = len(libraries)
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
def compare_gene_lib_results(request):
	# order_by = request.GET.get('order_by', 'library__library_code')
	gene_string = request.GET.get('s')
	genes = gene_string.split()
	# genome_id = request.GET.get('genome')
	library_data = request.GET.getlist('check')

	library = []
	genome_id = []
	for each in library_data:
		data = each.split('_')
		library.append(data[0])

		if data[1] not in genome_id:
			genome_id.append(data[1])

	test = {}
	for gene in genes:
		try:
			cds_fmin = Feature.objects.values_list('fmin', flat=True).filter(geneid=gene, genome_id__in=genome_id, featuretype='CDS')[0]
			cds_fmax = Feature.objects.values_list('fmax', flat=True).filter(geneid=gene, genome_id__in=genome_id, featuretype='CDS')[0]
		except IndexError:
			cds_fmin = 0
			cds_fmax = 0

		try:
			fmin = Feature.objects.filter(geneid=gene, genome_id__in=genome_id).filter(featuretype='gene').values('fmin')[0]
			fmax = Feature.objects.filter(geneid=gene, genome_id__in=genome_id).filter(featuretype='gene').values('fmax')[0]
		except IndexError:
			fmin = 0
			fmax = 0

		chromosome = Feature.objects.filter(geneid=gene, genome_id__in=genome_id).filter(featuretype='gene').values_list('chromosome', flat=True)[0]

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
	sorted_snp_dict = sorted(snp_dict.items(), key=lambda y: y[1][order_by])
	return sorted_snp_dict


# Displays the search page for a snp summary by library and chromosome level.
def chromosome_library_snp_summary(request):
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

	return render_to_response('snpdb/chromosome_library_snp_summary.html', {"results": results,
	                                                                        "paginator": paginator,
	                                                                        "ref_genome": ref_genome,
	                                                                        "toolbar_max": toolbar_max,
	                                                                        "toolbar_min": toolbar_min})


# Returns a chromosome level summary for an individual library.
def chromosome_library_snp_summary_filter(request):
	order_by = request.GET.get('order_by', 'chromosome__chromosome_name')
	library = request.GET.get('library')
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


# todo change to access genes through the Effect table.
# Returns a full list of genes found within a specific library. Currently connects through the feature table.
def gene_list(request):
	order_by = request.GET.get('order_by', 'start')
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
	full_chrom = request.GET.get('full_chrom')


	title = "SNP Region Summary"

	if full_chrom:
		genes = SNP.objects.filter(effect__effect__effect_name="Gene_Name").values('snp_position', 'effect__effect_string',
		                                                                           'effect__effect_group').filter(chromosome__chromosome_name=chrom,
		                                                                                                          library__library_code=library).distinct()

	else:
		genes = SNP.objects.filter(effect__effect__effect_name="Gene_Name").values('snp_position', 'effect__effect_string',
		                                                                           'effect__effect_group').filter(chromosome__chromosome_name=chrom,
		                                                                                                          library__library_code=library,
		                                                                                                          snp_position__range=(start, stop)).distinct()

	results = defaultdict(int)
	for each in genes:
		effect_group = each['effect__effect_group']
		impact = SNP.objects.filter(effect__effect__effect_name="Annotation_Impact",
		                            effect__effect_group=effect_group,
		                            snp_position=each['snp_position'],
		                            chromosome__chromosome_name=chrom,
		                            library__library_code=library).values('snp_position', 'ref_base', 'alt_base', 'heterozygosity',
		                                                                  'quality', 'effect__effect_string', 'effect__effect_class').distinct()

		for x in impact:
			x['gene'] = each['effect__effect_string']
			if each['snp_position'] in results:
				results[each['snp_position']].append(x)
			else:
				results[each['snp_position']] = [x,]

	page = request.GET.get('page')
	paginator = Paginator(results.items(), 50)

	count = len(results)

	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)
	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)

	return render_to_response('snpdb/chrom_region_filter.html', {"chromosome": chrom,
	                                                             "library": library,
	                                                             "title": title,
	                                                             "count":count,
	                                                             "results": results,
	                                                             "toolbar_max": toolbar_max,
	                                                             "toolbar_min": toolbar_min}, context_instance=RequestContext(request))


# Dumps a queryset into a csv file.
def dump(qs, outfile_path):
	keys = []
	values = []
	for obj in qs:
		if isinstance(obj, dict):
			for key, val in obj.items():
				if isinstance(val, int):
					values.append(val)
				else:
					values.append(val.encode("UTF8").replace('_', ' ').replace('&', ' and ',))

				if key not in keys:
					keys.append(key)
			value = [list(values[i:i+2]) for i in range(0, len(values), 2)]

		elif isinstance(obj, tuple):


			if obj[1] == "HIGH":
				val = "Changes to CDS Length"
			elif obj[1] == "LOW":
				val = "Synonymous Changes"
			elif obj[1] == "MODERATE":
				val = "Non-Synonymous Changes"
			elif obj[1] == "MODIFIER":
				val = "Non-CDS Changes"
			else:
				val = "n/a"
			values.append(val)

			if "Impact" not in keys:
				keys.append("Impact")
				keys.append("snp_count")
			if isinstance(obj[0], int) or isinstance(obj[0], long):
				values.append(obj[0])
			else:
				values.append(obj[0].encode("UTF8").replace('_', ' ').replace('&', ' and ',))

			value = [list(values[i:i+2]) for i in range(0, len(values), 2)]

	writer = csv.writer(open(outfile_path, 'w+'))

	print keys, values, value
	writer.writerow(keys)
	for each in value:
		writer.writerow(each)



	return value


# Reads a csv file and converts the data back into a dictionary.
def read(filename):
	impact_dict = {}
	for x in csv.reader(open(filename)):
		key = x[0]
		value = x[1]
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

	high_values = []
	low_values = []
	moderate_values = []
	modifier_values = []
	impact_values = []

	# high = Effect.objects.filter(effect__effect_name="Annotation_Impact", effect_string="HIGH").values("effect_class").annotate(Count('snp'))
	# high_list = dump(high, chart_path % 'high')
	#
	# high_snp_total = sum(i[1] for i in high_list)
	#
	# for each in high_list:
	# 	high_labels.append(each[0] + ': ' + str(round(float(each[1])/float(high_snp_total)*100, 2)) + '%')
	# 	high_values.append(round(float(each[1])/float(high_snp_total)*100, 2))
	#
	#
	# snps_by_high_impact = Pie(high_values).label(*high_values).legend(*high_labels).legend_pos('l').color("919dab", "D2E3F7",
	#                                                                                                       "658CB9", "88BBF7",
	#                                                                                                       "666E78").size(800,350)
	# snps_by_high_impact.image().save(image_path % 'high', 'png')
	# print "high files saved"

	cursor = connection.cursor()
	cursor.execute("""SELECT count(snp_id), effect_string
  				FROM snpdb_effect
				WHERE effect_id = 64
				GROUP BY effect_string
				ORDER BY effect_string""")

	impact = cursor.fetchall()

	impact_list = dump(impact, chart_path % 'impact')

	impact_snp_total = sum(i[1] for i in impact_list)

	for each in impact_list:
		impact_labels.append(each[0] + ': ' + str(round(float(each[1])/float(impact_snp_total)*100, 2)) + '%')
		impact_values.append(round(float(each[1])/float(impact_snp_total)*100, 2))


	snps_by_impact = Pie(impact_values).label(*impact_values).legend(*impact_labels).legend_pos('l').color("919dab", "D2E3F7",
	                                                                                                       "658CB9", "88BBF7",
	                                                                                                       "666E78").size(800,350)
	snps_by_impact.image().save(image_path % 'impact', 'png')
	print "impact files saved"

	low = Effect.objects.filter(effect__effect_name="Annotation_Impact", effect_string="LOW").values("effect_class").annotate(Count('snp'))
	low_list = dump(low, chart_path % 'low')

	low_snp_total = sum(i[1] for i in low_list)

	for each in low_list:
		low_labels.append(each[0] + ': ' + str(round(float(each[1])/float(low_snp_total)*100, 2)) + '%')
		low_values.append(round(float(each[1])/float(low_snp_total)*100, 2))

	snps_by_low = Pie(low_values).label(*low_values).legend(*low_labels).legend_pos('l').color("919dab", "D2E3F7",
	                                                                                           "658CB9", "88BBF7",
	                                                                                           "666E78").size(800,350)
	snps_by_low.image().save(image_path % 'low', 'png')
	print "low files saved"

	moderate = Effect.objects.filter(effect__effect_name="Annotation_Impact", effect_string="MODERATE").values("effect_class").annotate(Count('snp'))
	moderate_list = dump(moderate, chart_path % 'moderate')

	moderate_snp_total = sum(i[1] for i in moderate_list)

	for each in moderate_list:
		moderate_labels.append(each[0] + ': ' + str(round(float(each[1])/float(moderate_snp_total)*100, 2)) + '%')
		moderate_values.append(round(float(each[1])/float(moderate_snp_total)*100, 2))

	snps_by_moderate = Pie(moderate_values).label(*moderate_values).legend_pos('l').legend(*moderate_labels).color("919dab", "D2E3F7",
	                                                                                                               "658CB9", "88BBF7",
	                                                                                                               "666E78").size(800,350)
	snps_by_moderate.image().save(image_path % 'moderate', 'png')
	print "moderate files saved"

	modifier = Effect.objects.filter(effect__effect_name="Annotation_Impact", effect_string="MODIFIER").values("effect_class").annotate(Count('snp'))
	modifier_list = dump(modifier, chart_path % 'modifier')

	modifier_snp_total = sum(i[1] for i in modifier_list)

	for each in modifier_list:
		modifier_labels.append(each[0] + ': ' + str(round(float(each[1])/float(modifier_snp_total)*100, 2)) + '%')
		modifier_values.append(round(float(each[1])/float(modifier_snp_total)*100, 2))

	snps_by_modifier = Pie(modifier_values).label(*modifier_values).legend_pos('l').legend(*modifier_labels).color("919dab", "D2E3F7",
	                                                                                                               "658CB9", "88BBF7",
	                                                                                                               "666E78").size(800,350)
	snps_by_modifier.image().save(image_path % 'modifier', 'png')
	print "modifier files saved"

	lib_count = SNP.objects.values("library__library_code").distinct().annotate(Count('snp_id'))
	lib_snps = []
	lib_snp_total = 0
	for each in lib_count.iterator():
		lib_snps.append(each['snp_id__count'])
		lib_snp_total += each['snp_id__count']
		lib_legend.append(each['library__library_code'])
	for x in lib_snps:
		percentage = float(x)/float(lib_snp_total)*100
		lib_labels.append(round(percentage, 2))

	snps_by_library = Pie([lib_labels]).label(*lib_labels).legend_pos('l').legend(*lib_legend).color("919dab", "D2E3F7",
	                                                                                                 "658CB9", "88BBF7",
	                                                                                                 "666E78").size(800,350)
	snps_by_library.image()
	snps_by_library.image().save(image_path % 'library', 'png')
	print "saved snps_by_library"

	org_count = SNP.objects.values("result__genome__organism__organismcode").distinct().annotate(Count('snp_id'))
	org_snps = []
	org_snp_total = 0
	for each in org_count.iterator():
		org_snps.append(each['snp_id__count'])
		org_snp_total += each['snp_id__count']
	for x in org_snps:
		percentage = float(x)/float(org_snp_total)*100
		org_labels.append(round(percentage, 2))
	org_legend.append(each['result__genome__organism__organismcode'])
	snps_by_organism = Pie(org_labels).label(*org_labels).legend_pos('l').legend(*org_legend).color("919dab", "D2E3F7",
	                                                                                                "658CB9", "88BBF7",
	                                                                                                "666E78").size(800,350)
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
