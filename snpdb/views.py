from django.shortcuts import render
from django.http import HttpResponse
from snpdb.models import *
from django.template import loader, Context
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from utils import build_orderby_urls, integer_filters
from django.db import connection


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

