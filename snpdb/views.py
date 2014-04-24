from django.shortcuts import render
from django.http import HttpResponse
from snpdb.models import *
from django.template import loader, Context
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from utils import build_orderby_urls, integer_filters
from django.db import connection


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
        filter = paginator.page(page)
    except PageNotAnInteger:
        filter = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    toolbar_max = min(filter.number + 4, paginator.num_pages)
    toolbar_min = min(filter.number - 4, 0)

    return render_to_response('snpdb/filter.html', {"filter": filter,
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
            result_list = SNP.objects.filter(heterozygosity__regex=filter_on)
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
            result_list = SNP.objects.all().filter().filter(snp_position=filter_on)
        elif selection == 'Result':
            result_list = SNP.objects.all().filter()(result=filter_on)
        elif selection == 'Reference Base':
            result_list = SNP.objects.all().filter(ref_base=filter_on)
        elif selection == 'Alternative Base':
            result_list = SNP.objects.all().filter(alt_base=filter_on)
        elif selection == 'Heterozygosity':
            result_list = SNP.objects.all().filter(heterozygosity=filter_on)
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
    paginator = Paginator(result_list, 50)
    page = request.GET.get('page')
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
