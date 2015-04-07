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
from django.forms.models import ModelChoiceField

EXPERIMENT_TYPE_CHOICES = (
    ('SL', 'SL'),
    ('RNAseq', 'RNAseq'),
    ('RiboProf', 'RiboProf'),
    ('DNAseq', 'DNAseq'),
    ('mixed', 'mixed')
)

class ExptrefgenomeChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return unicode(obj.refgenome)

class ExpttypeChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return unicode(obj.type)


def GetChoiceValueTuple(queryset, fieldname):
        values = queryset.values_list(fieldname, flat=True)
        unique_values = ['ALL']
        [unique_values.append(item) for item in values if item not in unique_values]
        choice_list = []
        for item in unique_values:
            choice_list.append(tuple([item, item]))
        return tuple(choice_list)

class ListExperiemntsForm(forms.Form):
    expttype = forms.ChoiceField(choices=GetChoiceValueTuple(Experiment.objects.all(), 'type'))
    refgenome = forms.ChoiceField(choices=GetChoiceValueTuple(Organism.objects.all(), 'organismcode'))
    collaborator = forms.ChoiceField(choices=GetChoiceValueTuple(Collaborator.objects.all(), 'lastname'))

#============================================================================#
# View helper functions
#============================================================================#
def get_samplecodes_fromlibcodes(request, libcodes):
    samplecodes=[]
    for libcode in libcodes:
        samplecodes.append(Library.objects.get(library_code=libcode).sampleid.sampleid)
    return samplecodes

def get_samplecode_fromlibcode(request, libcode):
    samplecode = Library.objects.get(library_code=libcode).sampleid.sampleid
    return samplecode

def get_libcodes_fromexpid(request, expid):
    experiment = Experiment.objects.get(id=expid)
    samples = experiment.samples.all()
    library_codes = []
    for sampleobj in samples:
        libcodes = sampleobj.library_set.all().values_list('library_code', flat=True)
        for libcode in libcodes:
            library_codes.append(libcode)
    return library_codes

def get_libcode_samplename_map(request, libcodes):
    map = {}
    for libcode in libcodes:
         map[libcode]=Library.objects.get(library_code=libcode).sampleid.samplename
    return map




#============================================================================#
# View  functions
#============================================================================#
def ListSamples(request):
    '''
    List all loaded Samples. Allow exploration.
    :param request:
    :return: all Sample objects; with libraries made from them
    '''

    kwargs = {}
    #kwargs['user']=user
    kwargs['listoflinks']=listoflinks
    kwargs['title']="Samples List"


    if request.method == 'POST':
        form = ListExperiemntsForm(request.POST) #bound form
        if form.is_valid():
            expttype = form.cleaned_data['expttype']
            refgenome = form.cleaned_data['refgenome']
            collaboratorLN = form.cleaned_data['collaborator']

            # get experiments

            expts = Experiment.objects.all()
            if expttype != 'ALL':
                expts = expts.filter(type=expttype)
            if refgenome != 'ALL':
                expts = expts.filter(refgenome__organism__organismcode=refgenome)
            if collaboratorLN != 'ALL':
                expts = expts.filter(collaborator__lastname=collaboratorLN)

            expts_RNAseq = expts.filter(type='RNAseq')
            expts_DNAseq = expts.filter(type='DNAseq')
            expts_SLseq = expts.filter(type='SL')

            kwargs['experiments']=expts
            kwargs['expts_RNAseq']=expts_RNAseq
            kwargs['expts_DNAseq']=expts_DNAseq
            kwargs['expts_SLseq']=expts_SLseq
            print expts_RNAseq

            kwargs['form']=form
        else:
            kwargs['form']=form
    else:
        form = ListExperiemntsForm() #un bound form
        kwargs['form']=form



    return render_to_response('ngsdbview/experiment_list.html',kwargs, context_instance=RequestContext(request))


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


    if request.method == 'POST':
        form = ListExperiemntsForm(request.POST) #bound form
        if form.is_valid():
            expttype = form.cleaned_data['expttype']
            refgenome = form.cleaned_data['refgenome']
            collaboratorLN = form.cleaned_data['collaborator']

            # get experiments

            expts = Experiment.objects.all()
            if expttype != 'ALL':
                expts = expts.filter(type=expttype)
            if refgenome != 'ALL':
                expts = expts.filter(refgenome__organism__organismcode=refgenome)
            if collaboratorLN != 'ALL':
                expts = expts.filter(collaborator__lastname=collaboratorLN)

            expts_RNAseq = expts.filter(type='RNAseq')
            expts_DNAseq = expts.filter(type='DNAseq')
            expts_SLseq = expts.filter(type='SL')

            kwargs['experiments']=expts
            kwargs['expts_RNAseq']=expts_RNAseq
            kwargs['expts_DNAseq']=expts_DNAseq
            kwargs['expts_SLseq']=expts_SLseq
            print expts_RNAseq

            kwargs['form']=form
        else:
            kwargs['form']=form
    else:
        form = ListExperiemntsForm() #un bound form
        kwargs['form']=form



    return render_to_response('ngsdbview/experiment_list.html',kwargs, context_instance=RequestContext(request))


def ExperimentDetailRNAseq(request, experimentId):
    '''
    Detail an experiment.
    :param request:
    :return: one experimental object
    '''

    kwargs = {}
    #kwargs['user']=user
    kwargs['listoflinks']=listoflinks
    kwargs['title']="Experiment Detail"
    #experimentId = "42"
    # get experiments
    exp = Experiment.objects.get(id=experimentId)
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
    return render_to_response('ngsdbview/experiment_detail_RNAseq.html',kwargs, context_instance=RequestContext(request))


def ExperimentDetailDNAseq(request, experimentId):
    '''
    Detail an experiment.
    :param request:
    :return: one experimental object
    '''

    kwargs = {}
    #kwargs['user']=user
    kwargs['listoflinks']=listoflinks
    kwargs['title']="Experiment Detail"
    #experimentId = "42"
    # get experiments
    exp = Experiment.objects.get(id=experimentId)
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
    return render_to_response('ngsdbview/experiment_detail_DNAseq.html',kwargs, context_instance=RequestContext(request))


def ExperimentDetailSLseq(request, experimentId):
    '''
    Detail an experiment.
    :param request:
    :return: one experimental object
    '''

    kwargs = {}
    #kwargs['user']=user
    kwargs['listoflinks']=listoflinks
    kwargs['title']="Experiment Detail"
    #experimentId = "42"
    # get experiments
    exp = Experiment.objects.get(id=experimentId)
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
    return render_to_response('ngsdbview/experiment_detail_SLseq.html',kwargs, context_instance=RequestContext(request))


def SNPCompareLibs(request, experimentId):
    '''
    Compare SNPs from two libraries.
    :param request:
    :return: link to Marea's snp analysis
    '''

    kwargs = {}
    #kwargs['user']=user
    kwargs['listoflinks']=listoflinks
    kwargs['title']="Compare SNPs between two sets of libraries (of an experiment)"

    # get experiments
    exp = Experiment.objects.get(id=experimentId)
    kwargs['exp'] = exp
    libcodes = get_libcodes_fromexpid(request, experimentId)
    kwargs['libcodes'] = libcodes

    kwargs['libcode_name_map'] = get_libcode_samplename_map(request, libcodes)

    print kwargs['libcodes']
    return render_to_response('ngsdbview/snp_compare_libraries.html', kwargs, context_instance=RequestContext(request))


def ListCollaborators(request):
    """
    List all loaded collaborators. Allow exploration.
    :param request:
    :return: all collaborator objects;
    """

    kwargs = {}
    #kwargs['user']=user
    kwargs['listoflinks']=listoflinks
    kwargs['title']="Collaborator List"

    kwargs['collaborators'] = Collaborator.objects.all()

    return render_to_response('ngsdbview/collaborators_list.html',kwargs, context_instance=RequestContext(request))

def ListOrganisms(request):
    """
    List all loaded Organisms. Allow exploration.
    :param request:
    :return: all Organisms objects;
    """

    kwargs = {}
    #kwargs['user']=user
    kwargs['listoflinks']=listoflinks
    kwargs['title']="Organisms List"

    kwargs['organisms'] = Organism.objects.all()

    return render_to_response('ngsdbview/organisms_list.html',kwargs, context_instance=RequestContext(request))


def ListGenomes(request):
    """
    List all loaded Genomes. Allow exploration.
    :param request:
    :return: all Genomes objects;
    """

    kwargs = {}
    #kwargs['user']=user
    kwargs['listoflinks']=listoflinks
    kwargs['title']="Genomes List"

    kwargs['genomes'] = Genome.objects.all()

    return render_to_response('ngsdbview/genomes_list.html',kwargs, context_instance=RequestContext(request))
