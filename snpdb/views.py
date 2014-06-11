from snpdb.models import *
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from utils import build_orderby_urls, integer_filters
from django.db.models import *
from django_boolean_sum import BooleanSum
from templatetags.snp_filters import *


def dashboard(request):
    return render_to_response('snpdb/dashboard.html')


def effect(request):
    order_by = request.GET.get('order_by', 'effect')
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
        contacts = paginator.page(paginator.num_pages)

    toolbar_max = min(snp_effect.number + 4, paginator.num_pages)
    toolbar_min = max(snp_effect.number - 4, 0)

    return render_to_response('snpdb/effect.html', {"snp_effect": snp_effect,
                                                    "filter_urls": filter_urls,
                                                    "paginator": paginator,
                                                    "toolbar_max": toolbar_max,
                                                    "toolbar_min": toolbar_min})


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
        contacts = paginator.page(paginator.num_pages)

    toolbar_max = min(filters.number + 3, paginator.num_pages)
    toolbar_min = max(filters.number - 3, 0)
    return render_to_response('snpdb/filter.html', {"filters": filters,
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
        contacts = paginator.page(paginator.num_pages)

    toolbar_max = min(statistic.number + 3, paginator.num_pages)
    toolbar_min = max(statistic.number - 3, 0)

    return render_to_response('snpdb/statistics.html', {"statistic": statistic,
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
        contacts = paginator.page(paginator.num_pages)

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
        contacts = paginator.page(paginator.num_pages)

    toolbar_max = min(snptypes.number + 4, paginator.num_pages)
    toolbar_min = max(snptypes.number - 4, 0)

    return render_to_response('snpdb/snptype.html', {"snptypes": snptypes,
                                                     "filter_urls": filter_urls,
                                                     "paginator": paginator,
                                                     "toolbar_max": toolbar_max,
                                                     "toolbar_min": toolbar_min})


# Search views
#---------------------------------------------------------------------------------------------------
def snp_filter_result(request):
    selection = request.GET.get('att')
    filter_on = request.GET.get('s')
    check = request.GET.get('check')
    if check == "on":
        if selection == 'SNP Position':
            positions = integer_filters(SNP.objects.values_list('snp_position'), filter_on, selection)
            result_list = SNP.objects.all().filter(snp_position__in=positions)
        elif selection == 'Result':
            result_list = SNP.objects.all().filter(result__regex=filter_on)
        elif selection == 'Reference Base':
            result_list = SNP.objects.filter(ref_base__regex=filter_on)
        elif selection == 'Alternative Base':
            result_list = SNP.objects.filter(alt_base__regex=filter_on)
        elif selection == 'Heterozygosity':
            if filter_on == 'False':
                result_list = SNP.objects.all().filter(heterozygosity=False)
            elif filter_on == 'True':
                result_list = SNP.objects.all().filter(heterozygosity=True)
        elif selection == 'Quality':
            qualities = integer_filters(SNP.objects.values_list('qualities'), filter_on, selection)
            result_list = SNP.objects.filter(quality__in=qualities)
        elif selection == 'Library':
            result_list = SNP.objects.filter(library_id__regex=filter_on)
        elif selection == 'Chromosome':
            result_list = SNP.objects.filter(chromosome_id__regex=filter_on)
        else:
            result_list = SNP.objects.all()
    else:
        if selection == 'SNP Position':
            result_list = SNP.objects.all().filter(snp_position=filter_on)
        elif selection == 'Result':
            result_list = SNP.objects.all().filter(result=filter_on)
        elif selection == 'Reference Base':
            result_list = SNP.objects.all().filter(ref_base=filter_on)
        elif selection == 'Alternative Base':
            result_list = SNP.objects.all().filter(alt_base=filter_on)
        elif selection == 'Heterozygosity':
            if filter_on == 'False':
                result_list = SNP.objects.all().filter(heterozygosity=False)
            elif filter_on == 'True':
                result_list = SNP.objects.all().filter(heterozygosity=True)
        elif selection == 'Quality':
            result_list = SNP.objects.all().filter(quality=filter_on)
        elif selection == 'Library':
            result_list = SNP.objects.all().filter(library_id=filter_on)
        elif selection == 'Library':
            result_list = SNP.objects.all().filter(chromosome_id=filter_on)
        else:
            result_list = SNP.objects.all()

    order_by = request.GET.get('order_by', 'snp_id')
    result_list = result_list.order_by(order_by)
    filter_urls = build_orderby_urls(request.get_full_path(), ['snp_id', 'snp_position', 'result',
                                                               'ref_base', 'alt_base', 'heterozygosity',
                                                               'quality', 'library', 'chromosome'])
    paginator = Paginator(result_list, 50)
    page = request.GET.get('page')

    try:
        snps = paginator.page(page)
    except PageNotAnInteger:
        snps = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    toolbar_max = min(snps.number + 3, paginator.num_pages)
    toolbar_min = max(snps.number - 3, 0)

    return render_to_response('snpdb/snp.html', {"snps": snps,
                                                 "filter_urls": filter_urls,
                                                 "paginator": paginator,
                                                 "toolbar_max": toolbar_max,
                                                 "toolbar_min": toolbar_min})


def effect_filter(request):
    selection = request.GET.get('att')
    filter_on = request.GET.get('s')
    check = request.GET.get('check')
    if check == "on":
        if selection == 'SNP ID':
            positions = integer_filters(Effect.objects.values_list('snp_id'), filter_on, selection)
            result_list = Effect.objects.all().filter(snp_id__in=positions)
        elif selection == 'Effect Type':
            result_list = Effect.objects.all().filter(effect__regex=filter_on)
        elif selection == 'Effect Class':
            result_list = Effect.objects.filter(effect_class__regex=filter_on)
        elif selection == 'Effect':
            result_list = Effect.objects.filter(effect_string__regex=filter_on)
        elif selection == 'Effect Group':
            positions = integer_filters(Effect.objects.values_list('effect_group'), filter_on, selection)
            result_list = Effect.objects.all().filter(effect_group__in=positions)
        else:
            result_list = Effect.objects.all()
    else:
        if selection == 'SNP ID':
            result_list = Effect.objects.all().filter(snp_id=filter_on)
        elif selection == 'Effect Type':
            result_list = Effect.objects.all().filter(effect=filter_on)
        elif selection == 'Effect Class':
            result_list = Effect.objects.all().filter(effect_class=filter_on)
        elif selection == 'Effect':
            result_list = Effect.objects.all().filter(effect_string=filter_on)
        elif selection == 'Effect Group':
            result_list = Effect.objects.all().filter(effect_group=filter_on)
        else:
            result_list = Effect.objects.all()

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
        contacts = paginator.page(paginator.num_pages)

    toolbar_max = min(snp_effect.number + 3, paginator.num_pages)
    toolbar_min = max(snp_effect.number - 3, 0)

    return render_to_response('snpdb/effect.html', {"snp_effect": snp_effect,
                                                    "filter_urls": filter_urls,
                                                    "paginator": paginator,
                                                    "toolbar_max": toolbar_max,
                                                    "toolbar_min": toolbar_min})


def filter_filter(request):
    selection = request.GET.get('att')
    filter_on = request.GET.get('s')
    check = request.GET.get('check')
    if check == "on":
        if selection == 'SNP ID':
            positions = integer_filters(Filter.objects.values_list('snp_id'), filter_on, selection)
            result_list = Filter.objects.all().filter(snp_id__in=positions)
        elif selection == 'Filter ID':
            positions = integer_filters(Filter.objects.values_list('filter_id'), filter_on, selection)
            result_list = Filter.objects.all().filter(filter_id__in=positions)
        elif selection == 'Filter Result':
            if filter_on == 'False':
                result_list = Filter.objects.all().filter(filter_result=False)
            elif filter_on == 'True':
                result_list = Filter.objects.all().filter(filter_result=True)
        elif selection == 'Filter':
            result_list = Filter.objects.filter(filter__regex=filter_on)
        else:
            result_list = Filter.objects.all()
    else:
        if selection == 'SNP ID':
            result_list = Filter.objects.all().filter(snp_id=filter_on)
        elif selection == 'Filter ID':
            result_list = Filter.objects.all().filter(filter_id=filter_on)
        elif selection == 'Filter Result':
            if filter_on == 'False':
                result_list = Filter.objects.all().filter(filter_result=False)
            elif filter_on == 'True':
                result_list = Filter.objects.all().filter(filter_result=True)
        elif selection == 'Filter':
            result_list = Filter.objects.all().filter(filter=filter_on)
        else:
            result_list = Filter.objects.all()

    order_by = request.GET.get('order_by', 'snp')
    result_list = result_list.order_by(order_by)
    paginator = Paginator(result_list, 50)
    page = request.GET.get('page')
    filter_urls = build_orderby_urls(request.get_full_path(), ['snp_id', 'filter_id', 'filter_result',
                                                               'filter_cv'])
    try:
        filter_list = paginator.page(page)
    except PageNotAnInteger:
        filter_list = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    toolbar_max = min(filter_list.number + 3, paginator.num_pages)
    toolbar_min = max(filter_list.number - 3, 0)

    return render_to_response('snpdb/filter.html', {"filter_list": filter_list,
                                                    "filter_urls": filter_urls,
                                                    "paginator": paginator,
                                                    "toolbar_max": toolbar_max,
                                                    "toolbar_min": toolbar_min})


def snptype_filter(request):
    selection = request.GET.get('att')
    filter_on = request.GET.get('s')
    check = request.GET.get('check')
    if check == "on":
        if selection == 'SNP Type':
            positions = integer_filters(SNP_Type.objects.values_list('snptype_id'), filter_on, selection)
            result_list = SNP_Type.objects.all().filter(snptype_id__in=positions)
        elif selection == 'SNP ID':
            positions = integer_filters(SNP_Type.objects.values_list('snp_id'), filter_on, selection)
            result_list = SNP_Type.objects.all().filter(snp_id__in=positions)
        elif selection == 'Indel':
            if filter_on == 'False':
                result_list = SNP_Type.objects.all().filter(indel=False)
            elif filter_on == 'True':
                result_list = SNP_Type.objects.all().filter(indel=True)
        elif selection == 'Deletion':
            if filter_on == 'False':
                result_list = SNP_Type.objects.all().filter(deletion=False)
            elif filter_on == 'True':
                result_list = SNP_Type.objects.all().filter(deletion=True)
        elif selection == 'Is SNP':
            if filter_on == 'False':
                result_list = SNP_Type.objects.all().filter(is_snp=False)
            elif filter_on == 'True':
                result_list = SNP_Type.objects.all().filter(is_snp=True)
        elif selection == 'Monomorphic':
            if filter_on == 'False':
                result_list = SNP_Type.objects.all().filter(monomorphic=False)
            elif filter_on == 'True':
                result_list = SNP_Type.objects.all().filter(monomorphic=True)
        elif selection == 'Transition':
            if filter_on == 'False':
                result_list = SNP_Type.objects.all().filter(transition=False)
            elif filter_on == 'True':
                result_list = SNP_Type.objects.all().filter(transition=True)
        elif selection == 'SV':
            if filter_on == 'False':
                result_list = SNP_Type.objects.all().filter(sv=False)
            elif filter_on == 'True':
                result_list = SNP_Type.objects.all().filter(sv=True)
        else:
            result_list = SNP_Type.objects.all()
    else:
        if selection == 'SNP Type':
            result_list = SNP_Type.objects.all().filter().filter(snptype_id=filter_on)
        elif selection == 'SNP ID':
            result_list = SNP_Type.objects.all().filter()(snp_id=filter_on)
        elif selection == 'Indel':
            if filter_on == 'False':
                result_list = SNP_Type.objects.all().filter(indel=False)
            elif filter_on == 'True':
                result_list = SNP_Type.objects.all().filter(indel=True)
        elif selection == 'Deletion':
            if filter_on == 'False':
                result_list = SNP_Type.objects.all().filter(deletion=False)
            elif filter_on == 'True':
                result_list = SNP_Type.objects.all().filter(deletion=True)
        elif selection == 'Is SNP':
            if filter_on == 'False':
                result_list = SNP_Type.objects.all().filter(is_snp=False)
            elif filter_on == 'True':
                result_list = SNP_Type.objects.all().filter(is_snp=True)
        elif selection == 'Monomorphic':
            if filter_on == 'False':
                result_list = SNP_Type.objects.all().filter(monomorphic=False)
            elif filter_on == 'True':
                result_list = SNP_Type.objects.all().filter(monomorphic=True)
        elif selection == 'Transition':
            if filter_on == 'False':
                result_list = SNP_Type.objects.all().filter(transition=False)
            elif filter_on == 'True':
                result_list = SNP_Type.objects.all().filter(transition=True)
        elif selection == 'SV':
            if filter_on == 'False':
                result_list = SNP_Type.objects.all().filter(sv=False)
            elif filter_on == 'True':
                result_list = SNP_Type.objects.all().filter(sv=True)
        else:
            result_list = Filter.objects.all()

    order_by = request.GET.get('order_by', 'snp')
    result_list = result_list.order_by(order_by)
    paginator = Paginator(result_list, 50)
    page = request.GET.get('page')
    filter_urls = build_orderby_urls(request.get_full_path(), ['snp_id', 'filter_id', 'filter_result',
                                                               'filter_cv'])
    try:
        snptypes = paginator.page(page)
    except PageNotAnInteger:
        snptypes = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    toolbar_max = min(snptypes.number + 4, paginator.num_pages)
    toolbar_min = max(snptypes.number - 4, 0)

    return render_to_response('snpdb/snptype.html', {"snptypes": snptypes,
                                                     "filter_urls": filter_urls,
                                                     "paginator": paginator,
                                                     "toolbar_max": toolbar_max,
                                                     "toolbar_min": toolbar_min})


def statistics_filter(request):
    selection = request.GET.get('att')
    filter_on = request.GET.get('s')
    check = request.GET.get('check')
    if check == "on":
        if selection == 'Statistic ID':
            positions = integer_filters(Statistics.objects.values_list('stats_id'), filter_on, selection)
            result_list = Statistics.objects.all().filter(stats_id__in=positions)
        elif selection == 'SNP ID':
            positions = integer_filters(Statistics.objects.values_list('snp_id'), filter_on, selection)
            result_list = Statistics.objects.all().filter(snp_id__in=positions)
        elif selection == 'Statistic':
            result_list = Statistics.objects.filter(stats_cvterm__regex=filter_on)
        elif selection == 'Value':
            result_list = Statistics.objects.all().filter(cv_value__regex=filter_on)
        else:
            result_list = Statistics.objects.all()
    else:
        if selection == 'Statistic ID':
            result_list = Statistics.objects.all().filter(stats_id=filter_on)
        elif selection == 'SNP ID':
            result_list = Statistics.objects.all().filter(snp_id=filter_on)
        elif selection == 'Statistic':
            result_list = Statistics.objects.all().filter(stats_cvterm=filter_on)
        elif selection == 'Value':
            result_list = Statistics.objects.all().filter(cv_value=filter_on)
        else:
            result_list = Statistics.objects.all()

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
        contacts = paginator.page(paginator.num_pages)

    toolbar_max = min(statistic.number + 4, paginator.num_pages)
    toolbar_min = max(statistic.number - 4, 0)

    return render_to_response('snpdb/statistics.html', {"statistic": statistic,
                                                        "filter_urls": filter_urls,
                                                        "paginator": paginator,
                                                        "toolbar_max": toolbar_max,
                                                        "toolbar_min": toolbar_min})

# Query views.
# --------------------------------------------------------------------------------------


# The search view for the user to input a gene. Lists all gene ids for the user to choose from.
def gene_snps(request):
    genes = Feature.objects.values('geneid').distinct()
    paginator = Paginator(genes, 120)

    page = request.GET.get('page')
    try:
        genes = paginator.page(page)
    except PageNotAnInteger:
        genes = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
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
        contacts = paginator.page(paginator.num_pages)

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
        contacts = paginator.page(paginator.num_pages)
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
        contacts = paginator.page(paginator.num_pages)
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
        contacts = paginator.page(paginator.num_pages)

    toolbar_max = min(results.number + 4, paginator.num_pages)
    toolbar_min = max(results.number - 4, 0)

    return render_to_response('snpdb/library_snp_summary.html', {"results": results,
                                                                 "count": count,
                                                                 "filter_urls": filter_urls,
                                                                 "paginator": paginator,
                                                                 "toolbar_max": toolbar_max,
                                                                 "toolbar_min": toolbar_min }
    )


def library_snps(request):
    order_by = request.GET.get('order_by', 'snp_id').encode("ascii")
    library = request.GET.get('lib')
    count = request.GET.get('count')
    print library
    selection = request.GET.get('att')
    filter_on = request.GET.get('s')
    print selection, filter_on
    filter_dict = {}
    filter_dict[str(selection)] = str(filter_on)
    print filter_dict
    if filter_dict:
        if selection == 'effect__effect_string':
            results = SNP.objects.filter(effect__effect_id=6, effect__effect_string__exact=filter_on.decode('utf-8'), effect__effect_class__endswith='SYNONYMOUS_CODING'.decode('utf-8'), library__librarycode=library).values('library', 'library__librarycode', 'snp_id',
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

    snp_dict = {}
    for each in results:
        current_genes = []
        if each['library__librarycode'] == library:
            if empty_effect(each['effect__effect']) or each['effect__effect'] == 6:
                if empty_effect(each['effect__effect_class']) or (each['effect__effect_class'] == ('NON_SYNONYMOUS_CODING' or 'SYNONYMOUS_CODING')):
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
                            current_genes.append(str(each['effect__effect_string'].decode('UTF8').strip()))
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
            else:
                if each['snp_id'] in snp_dict:
                    pass
                else:
                    each["effect__effect_class"] = 'None'
                    each["effect__effect_string"] = 'None'
                    each["effect__effect"] = 'None'
                    snp_dict[each['snp_id']] = each
    sorted_snp_dict = sorted(snp_dict.items(), key=lambda x: x[1][order_by])
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
        contacts = paginator.page(paginator.num_pages)

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


# # Returns all snps found in the specific library.
# def library_snps(request):
#     order_by = request.GET.get('order_by', 'snp_id').encode("ascii")
#     library = request.GET.get('lib')
#     count = request.GET.get('count')
#
#     results = SNP.objects.values('library', 'library__librarycode', 'snp_id',
#                                  'snp_position', 'ref_base', 'alt_base',
#                                  'heterozygosity', 'quality',
#                                  'chromosome__chromosome_name', 'effect__effect_string',
#                                  'effect__effect_class', 'effect__effect').order_by(order_by)
#
#     snp_dict = {}
#     for each in results:
#         current_genes = []
#         # current_genes[:] = []
#         if each['library__librarycode'] == library:
#             if empty_effect(each['effect__effect']) or each['effect__effect'] == 6:
#                 if empty_effect(each['effect__effect_class']) or (each['effect__effect_class'] == ('NON_SYNONYMOUS_CODING' or 'SYNONYMOUS_CODING')):
#                     if each['snp_id'] in snp_dict:
#                         for k, v in snp_dict[each['snp_id']].iteritems():
#                             if k == 'effect__effect_string':
#                                 if type(v) is list:
#                                     for x in v:
#                                         current_genes.append(str(x))
#                                 else:
#                                     current_genes.append(str(v).strip())
#                         if each['effect__effect_string'] in current_genes:
#                             pass
#                         elif snp_dict[each['snp_id']]['effect__effect_string'] == 'None':
#                             snp_dict[each['snp_id']] = each
#                         else:
#                             current_genes.append(str(each['effect__effect_string'].strip()))
#                             each['effect__effect_string'] = current_genes
#                             snp_dict[each['snp_id']] = each
#                     else:
#                         snp_dict[each['snp_id']] = each
#                 else:
#                     if each['snp_id'] in snp_dict:
#                         pass
#                     else:
#                         each["effect__effect_class"] = 'None'
#                         each["effect__effect_string"] = 'None'
#                         each["effect__effect"] = 'None'
#                         snp_dict[each['snp_id']] = each
#             else:
#                 if each['snp_id'] in snp_dict:
#                     pass
#                 else:
#                     each["effect__effect_class"] = 'None'
#                     each["effect__effect_string"] = 'None'
#                     each["effect__effect"] = 'None'
#                     snp_dict[each['snp_id']] = each
#     sorted_snp_dict = sorted(snp_dict.items(), key=lambda x: x[1][order_by])
#     paginator = Paginator(sorted_snp_dict, 100)
#     page = request.GET.get('page')
#
#     # Calls utils method to append new filters or order_by to the current url
#     filter_urls = build_orderby_urls(request.get_full_path(), ['library', 'library__librarycode', 'snp_id',
#                                                                'snp_position', 'ref_base', 'alt_base',
#                                                                'heterozygosity', 'quality',
#                                                                'chromosome__chromosome_name',
#                                                                'effect__effect_string'])
#     try:
#         results = paginator.page(page)
#     except PageNotAnInteger:
#         results = paginator.page(1)
#     except EmptyPage:
#         contacts = paginator.page(paginator.num_pages)
#
#     toolbar_max = min(results.number + 4, paginator.num_pages)
#     toolbar_min = max(results.number - 4, 0)
#
#     return render_to_response('snpdb/library_snps.html', {"results": results,
#                                                           "library": library,
#                                                           "order_by": order_by,
#                                                           "filter_urls": filter_urls,
#                                                           "paginator": paginator,
#                                                           "toolbar_max": toolbar_max,
#                                                           "toolbar_min": toolbar_min,
#                                                           "count": count})


# Dispalys the search page to compare snps across libraries
def compare_gene_lib(request):
    libraries = Library.objects.values('librarycode').distinct()
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

    return render_to_response('snpdb/compare_gene_library.html', {"results": results,
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
        contacts = paginator.page(paginator.num_pages)

    toolbar_max = min(results.number + 4, paginator.num_pages)
    toolbar_min = max(results.number - 4, 0)

    return render_to_response('snpdb/compare_gene_library_filter.html', {"results": results,
                                                                         "gene": gene,
                                                                         "count": count,
                                                                         "filter_urls": filter_urls,
                                                                         "toolbar_max": toolbar_max,
                                                                         "toolbar_min": toolbar_min }
    )


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
    max_snps = 0
    count = 0
    # print result_list
    for each in result_list:
        snp_position = each['snp_position']
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
    paginator = Paginator(result_list, 50)
    page = request.GET.get('page')
    filter_urls = build_orderby_urls(request.get_full_path(), ['gene', 'fmin', 'fmax', 'snp_position', 'library__librarycode'])
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
                                                                                "snp_group": snp_group,
                                                                                "max_snps": range(max_snps),
                                                                                "filter_urls": filter_urls,
                                                                                "toolbar_max": toolbar_max,
                                                                                "toolbar_min": toolbar_min}
    )


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
        contacts = paginator.page(paginator.num_pages)
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
        contacts = paginator.page(paginator.num_pages)
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
    results = SNP.objects.values('chromosome__chromosome_name', 'library__librarysize', 'library_id', 'library__librarycode').filter(library__librarycode=library).distinct().annotate(num_snps=Count('snp_id'),
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
        contacts = paginator.page(paginator.num_pages)

    toolbar_max = min(results.number + 4, paginator.num_pages)
    toolbar_min = max(results.number - 4, 0)

    return render_to_response('snpdb/chromosome_library_snp_summary_filter.html', {"results": results,
                                                                                   "filter_urls": filter_urls,
                                                                                   "paginator": paginator,
                                                                                   "toolbar_max": toolbar_max,
                                                                                   "toolbar_min": toolbar_min
    })


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
        contacts = paginator.page(paginator.num_pages)
    toolbar_max = min(results.number + 4, paginator.num_pages)
    toolbar_min = max(results.number - 4, 0)

    return render_to_response('snpdb/library_chromosome_snp.html', {"results": results,
                                                                    "paginator": paginator,
                                                                    "toolbar_max": toolbar_max,
                                                                    "toolbar_min": toolbar_min})


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
        contacts = paginator.page(paginator.num_pages)
    toolbar_max = min(results.number + 4, paginator.num_pages)
    toolbar_min = max(results.number - 4, 0)

    return render_to_response('snpdb/gene_list.html', {"results": results,
                                                       "library": library,
                                                       "count": count,
                                                       "filter_urls": filter_urls,
                                                       "paginator": paginator,
                                                       "toolbar_max": toolbar_max,
                                                       "toolbar_min": toolbar_min})