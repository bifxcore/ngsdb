# from django.shortcuts import render
# from django.http import HttpResponse
from snpdb.models import *
# from django.template import loader, Context
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from utils import build_orderby_urls, integer_filters
# from django.db import connection


def dashboard(request):
    return render_to_response('snpdb/dashboard.html')


def effect(request):
    order_by = request.GET.get('order_by', 'snp')
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
    toolbar_min = min(snp_effect.number - 4, 0)

    return render_to_response('snpdb/effect.html', {"snp_effect": snp_effect,
                                                    "filter_urls": filter_urls,
                                                    "paginator": paginator,
                                                    "toolbar_max": toolbar_max,
                                                    "toolbar_min": toolbar_min})


def filter(request):
    order_by = request.GET.get('order_by', 'snp')
    filter_list = Filter.objects.all().order_by(order_by)

    paginator = Paginator(filter_list, 50)

    page = request.GET.get('page')

    # Calls utils method to append new filters or order_by to the current url
    filter_urls = build_orderby_urls(request.get_full_path(), ['snp_id', 'filter_id', 'filter_result',
                                                               'filter_cv'])
    try:
        filter_list = paginator.page(page)
    except PageNotAnInteger:
        filter_list = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    toolbar_max = min(filter_list.number + 4, paginator.num_pages)
    toolbar_min = min(filter_list.number - 4, 0)

    return render_to_response('snpdb/filter.html', {"filter_list": filter_list,
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

    toolbar_max = min(statistic.number + 4, paginator.num_pages)
    toolbar_min = min(statistic.number - 4, 0)

    return render_to_response('snpdb/statistics.html', {"statistic": statistic,
                                                        "filter_urls": filter_urls,
                                                        "paginator": paginator,
                                                        "toolbar_max": toolbar_max,
                                                        "toolbar_min": toolbar_min})


def snp(request):
    order_by = request.GET.get('order_by', 'snp_id')
    snp_list = SNP.objects.all().order_by(order_by)
    paginator = Paginator(snp_list, 50)
    page = request.GET.get('page')

    # Calls utils method to append new filters or order_by to the current url
    filter_urls = build_orderby_urls(request.get_full_path(), ['snp_id', 'snp_position', 'result',
                                                               'ref_base', 'alt_base', 'heterozygosity',
                                                               'quality', 'library', 'chromosome'])
    try:
        snps = paginator.page(page)
    except PageNotAnInteger:
        snps = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    toolbar_max = min(snps.number + 4, paginator.num_pages)
    toolbar_min = min(snps.number - 4, 0)

    return render_to_response('snpdb/snp.html', {"snps": snps,
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
    toolbar_min = min(snptypes.number - 4, 0)

    return render_to_response('snpdb/snptype.html', {"snptypes": snptypes,
                                                     "filter_urls": filter_urls,
                                                     "paginator": paginator,
                                                     "toolbar_max": toolbar_max,
                                                     "toolbar_min": toolbar_min})


# Search views
#---------------------------------------------------------------------------------------------------
def snp_filter(request):
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

    toolbar_max = min(snps.number + 4, paginator.num_pages)
    toolbar_min = min(snps.number - 4, 0)

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

    toolbar_max = min(snp_effect.number + 4, paginator.num_pages)
    toolbar_min = min(snp_effect.number - 4, 0)

    return render_to_response('snpdb/effect.html', {"snp_effect": snp_effect,
                                                    "filter_urls": filter_urls,
                                                    "paginator": paginator,
                                                    "toolbar_max": toolbar_max,
                                                    "toolbar_min": toolbar_min})


def filter_filter(request):
    selection = request.GET.get('att')
    filter_on = request.GET.get('s')
    check = request.GET.get('check')
    print selection
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
            print filter_on
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

    toolbar_max = min(filter_list.number + 4, paginator.num_pages)
    toolbar_min = min(filter_list.number - 4, 0)

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
    toolbar_min = min(snptypes.number - 4, 0)

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
    toolbar_min = min(statistic.number - 4, 0)

    return render_to_response('snpdb/statistics.html', {"statistic": statistic,
                                                        "filter_urls": filter_urls,
                                                        "paginator": paginator,
                                                        "toolbar_max": toolbar_max,
                                                        "toolbar_min": toolbar_min})


def gene_snps(request):
    genes = Feature.objects.values('geneid').distinct()
    paginator = Paginator(genes, 50)

    page = request.GET.get('page')
    try:
        genes = paginator.page(page)
    except PageNotAnInteger:
        genes = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    toolbar_max = min(genes.number + 4, paginator.num_pages)
    toolbar_min = min(genes.number - 4, 0)

    return render_to_response('snpdb/gene_to_snp.html', {"genes": genes,
                                                 "paginator": paginator,
                                                 "toolbar_max": toolbar_max,
                                                 "toolbar_min": toolbar_min})


def library_summary(request):
    results = SNP.objects.values('library_id', 'library__librarycode').distinct().annotate(num_snps=Count('snp_id'))
    order_by = request.GET.get('order_by', 'library')
    result_list = results.order_by(order_by)
    paginator = Paginator(result_list, 50)
    page = request.GET.get('page')

    # Calls utils method to append new filters or order_by to the current url
    filter_urls = build_orderby_urls(request.get_full_path(), ['library_id', 'librarycode', 'snp_id'])
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    toolbar_max = min(results.number + 4, paginator.num_pages)
    toolbar_min = min(results.number - 4, 0)

    return render_to_response('snpdb/library_snp_summary.html', {"results": results,
                                                 "filter_urls": filter_urls,
                                                 "paginator": paginator,
                                                 "toolbar_max": toolbar_max,
                                                 "toolbar_min": toolbar_min})


def gene_snps_filter(request):
    gene = request.GET.get('att')
    genome = Feature.objects.values('genome_id').filter(geneid=gene)
    results = SNP.objects.all().filter(result__in=(Result.objects.value('result_id').filter(result_id__in=genome)))
    print results
    return render_to_response('snpdb/gene_snps_filter.html', {"results": results,
                                                 "filter_urls": filter_urls,
                                                 "paginator": paginator,
                                                 "toolbar_max": toolbar_max,
                                                 "toolbar_min": toolbar_min})


