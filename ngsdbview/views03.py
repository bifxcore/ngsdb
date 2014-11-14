from ngsdbview.models import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from collections import defaultdict
from GChartWrapper import *
from django import forms
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from ngsdbview.viewtools import *
from django.contrib.auth.decorators import login_required
from samples.models import Library



def ListExperiments(request):
    '''
    List all loaded experiment. Allow exploration.
    :param request:
    :return: all experimental objects
    '''

    kwargs = {}
    #kwargs['user']=user
    kwargs['listoflinks']=listoflinks
    kwargs['title']="Experiments List"

    # get experiments
    kwargs['experiments'] = Experiment.objects.all()


    return render_to_response('ngsdbview/list_experiments.html',kwargs, context_instance=RequestContext(request))


def DetailExperiment(request):
    '''
    Detail an experiment.
    :param request:
    :return: one experimental object
    '''

    kwargs = {}
    #kwargs['user']=user
    kwargs['listoflinks']=listoflinks
    kwargs['title']="Experiment Detail"
    id = "42"
    # get experiments
    exp = Experiment.objects.get(id=id)
    kwargs['exp'] = exp

    comparisons = Comparison.objects.filter(experiment=exp)
    regulatedCount = defaultdict(lambda: defaultdict(int))
    for comparison in comparisons:
        dic = {}
        dic['Down Reg-2 Fold']=comparison.diffexpn_set.all().filter(pvalue__lte=0.01, log2foldchange__lte=-1).count()
        dic['Up Reg-2 Fold']=comparison.diffexpn_set.all().filter(pvalue__lte=0.01, log2foldchange__gte=1).count()
        dic['Down Reg-4Fold']=comparison.diffexpn_set.all().filter(pvalue__lte=0.01, log2foldchange__lte=-2).count()
        dic['Up Reg-4 Fold']=comparison.diffexpn_set.all().filter(pvalue__lte=0.01, log2foldchange__gte=2).count()
        regulatedCount[comparison.compname]=dic

    plotFileList = ['MDSfc_plot', 'allvsall_correlation_plot', 'BCV_plot', 'boxplot_normalized', 'boxplot_raw' ]
    plots = {}
    for fileName in  plotFileList:
        plots[fileName]=1

    kwargs['regulatedCount']=regulatedCount
    kwargs['plots']=plots
    return render_to_response('ngsdbview/detail_experiment.html',kwargs, context_instance=RequestContext(request))
