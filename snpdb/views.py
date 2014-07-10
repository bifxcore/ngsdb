from snpdb.models import *
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from utils import build_orderby_urls
from django.db.models import *
from django_boolean_sum import BooleanSum
from templatetags.snp_filters import *
from django.template import RequestContext

def dashboard(request):
    return render_to_response('snpdb/dashboard.html')


def test(request):
    return render_to_response('snpdb/test_header.html')


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
        effect = paginator.page(paginator.num_pages)

    toolbar_max = min(snp_effect.number + 4, paginator.num_pages)
    toolbar_min = max(snp_effect.number - 4, 0)

    return render_to_response('snpdb/effect.html', {"snp_effect": snp_effect,
                                                    "filter_urls": filter_urls,
                                                    "paginator": paginator,
                                                    "toolbar_max": toolbar_max,
                                                    "toolbar_min": toolbar_min,
                                                    "current_url": current_url},
                              context_instance=RequestContext(request))


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
        statistics = paginator.page(paginator.num_pages)

    toolbar_max = min(statistic.number + 3, paginator.num_pages)
    toolbar_min = max(statistic.number - 3, 0)

    return render_to_response('snpdb/statistics.html', {"statistic": statistic,
                                                        "filter_urls": filter_urls,
                                                        "paginator": paginator,
                                                        "toolbar_max": toolbar_max,
                                                        "toolbar_min": toolbar_min})


# Search views
#---------------------------------------------------------------------------------------------------
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
def compare_gene_lib_filter_results(request):
    order_by = request.GET.get('order_by', 'library__librarycode')
    gene = request.GET.get('s')
    library = request.GET.getlist('check')
    cds_fmin = Feature.objects.values_list('fmin', flat=True).filter(geneid=gene, featuretype='CDS')[0]
    cds_fmax = Feature.objects.values_list('fmax', flat=True).filter(geneid=gene, featuretype='CDS')[0]
    fmin = Feature.objects.filter(geneid=gene).filter(featuretype='gene').values('fmin')[0]
    fmax = Feature.objects.filter(geneid=gene).filter(featuretype='gene').values('fmax')[0]
    result_list = SNP.objects.values('snp_id', 'snp_position', 'ref_base', 'alt_base', 'library__librarycode').filter(library__librarycode__in=library,
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
        results = paginator.page(paginator.num_pages)
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
        else:
            print "library not same", library, each['library__librarycode']
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
                                 'library_id', 'library__librarycode').filter(library__librarycode=library).distinct().annotate(num_snps=Count('snp_id'),
                                                                                                                                hetero=BooleanSum('heterozygosity'),
                                                                                                                                indel=BooleanSum('snp_type__indel'),
                                                                                                                                trans=BooleanSum('snp_type__transition')).order_by(order_by)
    result_list = results.order_by(order_by)
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
                                                                     "toolbar_max": toolbar_max,
                                                                     "toolbar_min": toolbar_min})


def multi_gene_library_snps_filter(request):
    order_by = request.GET.get('order_by', 'effect__effect_string')
    gene = request.GET.get('s')
    libraries = request.GET.getlist('check')
    genes = gene.split()
    # libraries = library.split()
    print libraries

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


def difference_two_libraries(request):
    library1 = request.GET.get('lib1')
    library2 = request.GET.get('lib2')

    snp2 = SNP.objects.filter(library__librarycode=library2).values_list('snp_position',
                                                                         'chromosome__chromosome_name')
    snp1 = SNP.objects.filter(library__librarycode=library1).values_list('snp_position',
                                                                         'chromosome__chromosome_name')
    difference = set(snp1).difference(set(snp2))
    snps = []
    for x in difference:
        keys = ['snp_position', 'chromosome__chromosome_name']
        snps.append(dict(zip(keys, x)))

    snp_ids = []
    for each in snps:
        ids = SNP.objects.values_list('snp_id', flat=True).filter(library__librarycode=library1, snp_position=each['snp_position'],
                                                                  chromosome__chromosome_name=each['chromosome__chromosome_name'])
        snp_ids.append(ids)
    snp_id = [x for sublist in snp_ids for x in sublist]

    snp_impact = Effect.objects.filter(snp__in=snp_id, effect=1).values('effect_string').annotate(snp_count=Count('snp')).order_by('effect_string')
    effects = Effect.objects.filter(snp__in=snp_id, effect=1).values('effect', 'effect_class',
                                                                     'effect_string').annotate(effect_count=Count('snp')).order_by('effect_class')
    print "got modifier"
    return render_to_response('snpdb/impact_snps.html', {"effects": effects,
                                                         "snp_impact": snp_impact,
                                                         "library1": library1,
                                                         "library2": library2})


def impact_snps(request):
    order_by = request.GET.get('order_by', 'snp_id').encode("ascii")
    impact = request.GET.get('impact')
    library1 = request.GET.get('lib1')
    library2 = request.GET.get('lib2')

    snp2 = SNP.objects.filter(library__librarycode=library2).values_list('snp_position',
                                                                         'chromosome__chromosome_name')
    snp1 = SNP.objects.filter(library__librarycode=library1).values_list('snp_position',
                                                                         'chromosome__chromosome_name')
    difference = set(snp1).difference(set(snp2))
    snps = []
    for x in difference:
        keys = ['snp_position', 'chromosome__chromosome_name']
        snps.append(dict(zip(keys, x)))

    snp_ids = []
    for each in snps:
        ids = SNP.objects.values_list('snp_id', flat=True).filter(library__librarycode=library1, snp_position=each['snp_position'],
                                                                  chromosome__chromosome_name=each['chromosome__chromosome_name'])
        snp_ids.append(ids)
    snp_id = [x for sublist in snp_ids for x in sublist]

    snps = SNP.objects.filter(snp_id__in=snp_id, effect__effect_string=impact).values_list('snp_id', 'effect__effect_group')
    groups = []
    for y in snps:
        keys = ['snp_id', 'effect__effect_group']
        groups.append(dict(zip(keys, y)))
    genes = []
    for each in groups:
        genes.append(SNP.objects.filter(**each).values('library', 'library__librarycode', 'snp_id',
                                                       'snp_position', 'ref_base', 'alt_base',
                                                       'heterozygosity', 'quality', 'result_id',
                                                       'chromosome__chromosome_name', 'effect__effect_string',
                                                       'effect__effect_class', 'effect__effect'))
    print genes[:10]
    group = [x for sublist in genes for x in sublist]
    sorted_gene_dict = genes_from_effect(group, library1, order_by)
    gene_dict = [x for sublist in sorted_gene_dict for x in sublist]
    print len(filter(None, gene_dict))
    # new_dict = {k:v for k,v in gene_dict.items() if v}
    count = len(gene_dict)
    paginator = Paginator(gene_dict, 200)
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
    return render_to_response('snpdb/impact_snps_search.html', {"results": results,
                                                                "toolbar_max": toolbar_max,
                                                                "toolbar_min": toolbar_min,
                                                                "count": count,
                                                                "filter_urls": filter_urls,
                                                                })

