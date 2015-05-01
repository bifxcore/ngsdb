from snpdb.models import *
from samples.models import *
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext
from utils import build_orderby_urls


#============================================================================#
# CNV Query Views
#============================================================================#

def compare_cnv_libraries(request):
    ref_genome = request.GET.get('ref_genome')
    library_codes = request.GET.getlist('library_codes')
    chromosome = request.GET.getlist('chromosome')
    order_by = request.GET.get('order_by', 'start').encode('UTF8')

    if chromosome and library_codes:
        result_list = CNV.objects.values('start', 'stop', 'library__library_code',
                                         'coverage', 'cnv_value').filter(library__library_code__in=library_codes, cnv_type=1,
                                                                         chromosome__chromosome_name=chromosome[0])
        somy_list = CNV.objects.values('library__library_code',
                                       'cnv_value').filter(library__library_code__in=library_codes, cnv_type=2,
                                                           chromosome__chromosome_name=chromosome[0])

        somys = {}
        for each in somy_list:
            if each['library__library_code'].encode('UTF8') not in somys:
                somys[each['library__library_code'].encode('UTF8')] = each['cnv_value']


        cnv_dict = {}

        #Checks to see if tuples have all libraries present. Inserts blank tuples if not.
        for each in result_list:
            pos = chromosome[0] + '_' + str(each['start'])

            if pos in cnv_dict:
                library_dict = {'cnv': each['cnv_value'], 'coverage': each['coverage'], 'somy': somys[each['library__library_code'].encode('UTF8')]}

                if each['library__library_code'] not in cnv_dict[pos]:
                    cnv_dict[pos][each['library__library_code'].encode('UTF8')] = library_dict

            else:
                library_dict = {each['library__library_code'].encode('UTF8'): {'cnv': each['cnv_value'], 'coverage': each['coverage'], 'somy': somys[each['library__library_code'].encode('UTF8')]},
                                'start': each['start'], 'stop': each['stop']}
                cnv_dict[pos] = library_dict



        cnvs = cnv_dict.items()
        if order_by == 'cnv':
            lib =request.GET.get('lib').encode('UTF8')
            cnvs.sort(key=lambda (k, d): (d[lib], d['start'], ))
        else:
            cnvs.sort(key=lambda (k, d): (d[order_by], d['start'], ))

        # Calls utils method to append new filters or order_by to the current url
        filter_urls = build_orderby_urls(request.get_full_path(), ['chromosome', 'start', 'stop',
                                                                   'cnv', 'coverage', 'library', 'somy'])

        paginator = Paginator(cnvs, 50)
        page = request.GET.get('page')

        try:
            cnvs = paginator.page(page)
        except PageNotAnInteger:
            cnvs = paginator.page(1)
        except EmptyPage:
            cnvs = paginator.page(paginator.num_pages)

        toolbar_max = min(cnvs.number + 4, paginator.num_pages)
        toolbar_min = max(cnvs.number - 4, 0)

        return render_to_response('snpdb/compare_cnv_libraries.html', {"cnvs": cnvs,
                                                                       "somys": somys,
                                                                       "chromosome": chromosome[0],
                                                                       "ref_genome": ref_genome,
                                                                       "library_codes": library_codes,
                                                                       "filter_urls": filter_urls,
                                                                       "toolbar_max": toolbar_max,
                                                                       "toolbar_min": toolbar_min}, context_instance=RequestContext(request))

    elif library_codes and not chromosome:
        print library_codes, type(library_codes)
        chrom_list = Chromosome.objects.values('chromosome_name').filter(genome_name=ref_genome).order_by('chromosome_name')

        page = request.GET.get('page')
        paginator = Paginator(chrom_list, 500)

        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)
        toolbar_max = min(results.number + 4, paginator.num_pages)
        toolbar_min = max(results.number - 4, 0)
        return render_to_response('snpdb/compare_cnv_libraries.html', {"results": results,
                                                                       "library_codes": library_codes,
                                                                       "paginator": paginator,
                                                                       "toolbar_max": toolbar_max,
                                                                       "toolbar_min": toolbar_min},
                                  context_instance=RequestContext(request))

    elif ref_genome:
        lib_list = Library.objects.values('library_code',
                                          'result__genome__organism__organismcode').filter(result__genome__organism__organismcode=ref_genome).distinct().order_by('library_code')




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
    return render_to_response('snpdb/compare_cnv_libraries.html', {"results": results,
                                                                   "ref_genome": ref_genome,
                                                                   "paginator": paginator,
                                                                   "toolbar_max": toolbar_max,
                                                                   "toolbar_min": toolbar_min},
                              context_instance=RequestContext(request))