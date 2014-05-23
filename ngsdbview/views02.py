from ngsdbview.models import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from collections import defaultdict
from GChartWrapper import *
from django import forms
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from ngsdbview.viewtools import *
from django.contrib.auth.decorators import login_required

#============================================================================#
# View forms
#============================================================================#
class ListLibForm(forms.Form):
    """ form for searching libraries loaded into ngsdb """
    authordesignation = forms.CharField(max_length=20, label='Author Initials', required=False)
    organismcode = forms.CharField(max_length=20, label='Organism Code', required=False)
    libcode = forms.CharField(max_length=20, label='Library Code', required=False)


class ListAnalysesForm(forms.Form):
    ''' form for listing all analyses loaded into ngsdb '''
    authordesignation = forms.CharField(max_length=20, label='Author Initials', required=False)
    organismcode = forms.CharField(max_length=20, label='Organism Code', required=False)
    libcode = forms.CharField(max_length=20, label='Library Code', required=False)
    #iscurrentfield = forms.BooleanField(label='Current?', required=False,initial=True)
    #isobsfield = forms.BooleanField(label='Obsolete?', required=False, initial=False)

class GetResultsForGeneForm(forms.Form):
    geneid = forms.CharField(max_length=20, error_messages={'required': 'Please enter a Gene Id'})

class GetResultsForMultiGenesForm(forms.Form):
    libcode = forms.CharField(max_length=20, error_messages={'required': 'Please enter a Library code'})
    rank = forms.IntegerField(max_value=25, error_messages={'required': 'Please enter 0=> to display all sites; 1=>for major site and so on...'}, help_text="0=> to display all sites; 1=>for major site and so on..")
    geneidbox = forms.CharField(widget=forms.Textarea(), label="Geneid List", help_text="Ids separated by commma or semicolan or space or newline or any combination of these ")

datatype_choices = (
    ('raw', 'Site Level pileup; with NO gene association'),
    ('site', 'Site level pileup; with Gene association'),
    ('gene', 'Gene Level summary; with Gene association'),
)
class GetResultsForLibraryForm(forms.Form):
    libcode = forms.CharField(max_length=20, error_messages={'required': 'Please enter a Library code'})
    minreadcount = forms.IntegerField(initial=9)
    datatype = forms.ChoiceField(widget=RadioSelect, choices=datatype_choices)

class GetSitesForLibraryForm(forms.Form):
    libcode = forms.CharField(max_length=20, error_messages={'required': 'Please enter a Library code'})
    minreadcount = forms.IntegerField(initial=9, help_text="Minimum reads at the site choosen using rank field")
    rank = forms.IntegerField(initial=1, label="Rank of the site", help_text="1=>for major site; 2=>for second major site and so on...")

class GetSitecountMajorpcForLibsForm(forms.Form):
    libs = forms.CharField(max_length=200, error_messages={'required': 'Please enter set of librarycodes:'})


class GetResultsForMultiGenesMultiLibForm(forms.Form):
    rank = forms.IntegerField(max_value=25, help_text="1=>for major site; 2=>for second major site and so on..")
    geneidbox = forms.CharField(widget=forms.Textarea(), label="Geneid List", help_text="Ids separated by commma or semicolan or space or newline or any combination of these ")

class GetAlignStatsForm(forms.Form):
    pass

class PairLibrariesForm(forms.Form):
    normalize = forms.NullBooleanField()

from django.forms import ModelForm
#============================================================================#
# model forms
#============================================================================#




#============================================================================#
# View helper functions
#============================================================================#
def get_libgenome_dic(request, libcodes):
    libgenomedic={}
    for lib in libcodes:
        libgenomedic[lib] = get_genomes_for_lib(lib)
    libgenomedic

def get_genomes_for_lib(request, lib):
    dic = {}
    genomeobjs = Result.objects.filter(libraries__librarycode=lib).filter(is_current=True)
    for genomeobj in genomeobjs:
        dic[genomeobj.genome.organism.organismcode]= genomeobj.genome.source + genomeobj.genome.version
    return dic
def GetGenomeVersionForResid(request, resid):
    '''Get the Genome name and version for given resid'''
    resultobj = Result.objects.get(pk=resid)
    genome_version = resultobj.genome.organism.organismcode + '(' + resultobj.genome.version + ')'
    return genome_version

def GetGeneDesForGenomeid(request, genomeid):
    '''get all product names for given genome'''
    genedic={}
    featureobjs = Feature.objects.filter(genome=genomeid).filter(featuretype='gene')
    for feature in featureobjs:
        genedic[feature.geneid]=feature.geneproduct
    return genedic

def GetLibcodesForResid(request, resid):
    '''get all library codes for the given resid'''
    libcodes = Result.objects.get(pk=resid).libraries.all().values_list('librarycode', flat=True)
    return libcodes

def GetResidForLibcodeGenomeid(request, libcode, genomeid):
    '''get result id for the combination of library code and genomeid'''
    resultobj = Result.objects.filter(libraries__librarycode=libcode).filter(genome=genomeid).filter(is_current=True)
    resid=resultobj[0].result_id
    return resid

def GetResidForLibcodeGenomeVersion(request, libcode, genomecode, genomeversion):
    '''get result id for the combination of genomecode and geneome version'''
    resultobj = Result.objects.filter(libraries__librarycode=libcode).filter(genome__organism__organismcode=genomecode).filter(genome__version=genomeversion).filter(is_current=True)
    resid=resultobj[0].result_id
    return resid

def GroupLibcodesByGenome(request, libcodes):
    '''group given list of library codes by genome(and version) it aligned against'''
    genomelibcodemap = {}
    for libcode in libcodes:
        resultobjs = Result.objects.filter(libraries__librarycode=libcode).filter(is_current=True)
        for resultobj in resultobjs:
            #key is organism_version
            key = resultobj.genome.organism.organismcode+'_'+resultobj.genome.version
            if key in genomelibcodemap:
                genomelibcodemap[key].append(libcode)
            else:
                genomelibcodemap[key]=[libcode]

    return genomelibcodemap

def getChrByGeneid(request, geneid):
    '''
    Get chromosome from feature table using geneid alone
    caveat: Doest not distinguish between genome versions. Messes up if gene id jumped chrs between versions
    '''
    featureobj = Feature.objects.filter(geneid=geneid).filter(featuretype='gene')
    chr = featureobj[0].chromosome
    return chr

def getReadcountsForGeneResids(request, geneid, resids):
    '''Get gene objects for geneid and the result ids(list) passed here'''
    chr = getChrByGeneid(request, geneid)
    slsreadcount = {}
    # get  slsiteobjs for all resids and geneid & find all pos. across results for this gene
    slsiteobjs = Resultslsite.objects.filter(result__in=resids).filter(geneid=geneid)
    allpositions =[]
    for o in slsiteobjs:
        allpositions.append(o.position)

    # iterate all positions over resids to capture read count
    for resid in resids:
        posdic = {}
        for pos in allpositions:
            siteobjs = Resultslsite.objects.filter(result=resid).filter(position=pos).filter(chromosome=chr)
            if siteobjs:
                for sobj in siteobjs:
                    posdic[pos]=sobj.readcount
            else:
                posdic[pos]="0"
        slsreadcount[resid]=posdic
    return slsreadcount

def getIntervalsForGeneResid(request, geneid, resid, pos):
    ''' get a dic of intervals for given position in gene in resid    '''
    siteobjs = Resultslsite.objects.filter(result__result_id=resid).filter(geneid=geneid).filter(position=pos)
    interval = "NA"
    if siteobjs:
        interval = siteobjs[0].intervallength

    return  interval

def CreateAlignstat(request, libcode, resid, returntype):
    '''get lib size, mapping counts for pie chart'''
    libsize = Library.objects.filter(librarycode=libcode).values_list('librarysize', flat=True)[0]
    considered_reads = Resultprop.objects.filter(result__result_id=resid).filter(cvterm__name="number_reads_considered_for_alignment").values_list('value', flat=True)[0]
    uniquely_aligned_readcount = Resultprop.objects.filter(result__result_id=resid).filter(cvterm__name="number_reads_aligned_uniquely_to_reference_genome").values_list('value', flat=True)[0]
    unaligned_readcount = Resultprop.objects.filter(result__result_id=resid).filter(cvterm__name="number_reads_failed_to_align_to_reference_genome").values_list('value', flat=True)[0]
    nonuniquely_aligned_readcount = Resultprop.objects.filter(result__result_id=resid).filter(cvterm__name="number_reads_aligned_nonuniquely_to_reference_genome").values_list('value', flat=True)[0]
    totalaligned_readcount = int(uniquely_aligned_readcount) + int(nonuniquely_aligned_readcount)
    #calculate percentages
    uniqalignedperc  = round(100 * int(uniquely_aligned_readcount)/int(considered_reads))
    nonuniqalignedperc = round(100 * int(nonuniquely_aligned_readcount)/int(considered_reads))
    unalignedperc = round(100 * int(unaligned_readcount)/int(considered_reads))
    totalalignedperc = uniqalignedperc + nonuniqalignedperc
    alignstat=[uniquely_aligned_readcount, nonuniquely_aligned_readcount, unaligned_readcount]
    alignperc = [uniqalignedperc, nonuniqalignedperc, unalignedperc]

    # Create charts
    alinstatpiechart = Pie3D(alignstat).title('Align stat.\nRead counts').color('4d89f9', 'c6d9fd', 'ffcc99').label('Uniq', 'Non-Uniq', 'Unaligned').encoding('text')
    alinstatpiechart = str(alinstatpiechart) + '&chds=a'
    alinstatpiechart = alinstatpiechart.replace('chd=e', 'chd=t')
    alignstatdic = {
        'Uniquely aligned' : uniquely_aligned_readcount,
        'Non-Uniquely aligned' : nonuniquely_aligned_readcount,
        'Unaligned Reads' : unaligned_readcount,
        'Considered for Alignment' : considered_reads,
        'Original library size': libsize,
        'uniqalignedperc': uniqalignedperc,
        'nonuniqalignedperc': nonuniqalignedperc,
        'totalalignedperc': totalalignedperc,
        'Unaligned in Percentage': unalignedperc,
        'Total Aligned Reads': totalaligned_readcount,
        'Total Aligned in Percentage':str(totalalignedperc) + '(' + str(uniqalignedperc) + str(unalignedperc) + ')',
    }

    if returntype == 'chart':
        return alinstatpiechart
    elif returntype == 'data':
        return alignstatdic
    elif returntype == 'alignperc':
        return alignperc

def string2list(request, string):
    list1 = string.replace(',', ' ').replace(';', ' ').split()
    list1 = list(set(list1))

    return list1

#============================================================================#
# View functions
#============================================================================#

def PairLibraries(request):
    '''
    Funtion to pair count data from two or more libraries that are analyzed with same version of genome.
    Technically, one can compare across analysis done against different version of the same genome but with same gene ids.
    '''

    [user, availlibids] = getlibraries(request)
    kwargs = {}
    kwargs['user']=user
    kwargs['listoflinks']=listoflinks
    kwargs['title']="Pair Libraries"

    #
    # for autocomplete lib codes
    availlibcodes = Library.objects.filter(library_id__in=availlibids).values_list('librarycode', flat=True)
    autoclibcodes = constructAutocomplete('libcode',availlibcodes)
    kwargs['autoclibcodes'] = autoclibcodes

    if request.method == 'POST':
        form = PairLibrariesForm(request.POST) #bound form
        if form.is_valid():
            if 'libcodes' in request.POST:
                selectedlibcodes = request.POST.getlist('libcodes')
                kwargs['selectedlibcodes']=selectedlibcodes
                libgenomedic = get_libgenome_pairing(selectedlibcodes)

        else:
            kwargs['form'] = form
            kwargs['availlibcodes']=availlibcodes
    else:
        form = PairLibrariesForm() #unbound form
        kwargs['form']=form
        kwargs['availlibcodes']=availlibcodes

    return render_to_response('ngsdbview/pair_libraries.html',kwargs, context_instance=RequestContext(request))

@login_required
def Dashboard(request):
    '''
     function to display dashboard...contains summary stats. of the database
     '''

    #[user, availlibids] = getlibraries(request)
    kwargs = {}
    #kwargs['user']=user
    kwargs['listoflinks']=listoflinks
    kwargs['title']="Dashboard"

    libcount = Library.objects.all().count()
    anacount = Result.objects.all().count()
    kwargs['libcount'] = libcount
    kwargs['anacount'] = anacount

    libcountana = libcount
    analysedlibschart = Meter((libcount/libcountana)*100).label("Analysed").size(225,125)
    kwargs['analysedlibschart'] = analysedlibschart

    liborg = defaultdict(int)
    libtype = defaultdict(int)
    libauth = defaultdict(int)
    collaborators = defaultdict(int)

    libcodes = Library.objects.all().values_list('librarycode', flat=True)
    for libcode in libcodes:
        org = Organism.objects.filter(library__librarycode=libcode).values_list('organismcode', flat=True)[0]
        liborg[org] += 1
        type = Librarytype.objects.filter(library__librarycode=libcode).values_list('type', flat=True)[0]
        libtype[type] += 1
        author = Author.objects.filter(library__librarycode=libcode).values_list('designation', flat=True)[0]
        libauth[author] += 1
        (firstname, lastname) = Collaborator.objects.filter(library__librarycode=libcode).values_list('firstname', 'lastname')[0]
        collaborator = firstname + '_' + lastname
        collaborators[collaborator] += 1

    kwargs['libtype']=libtype
    kwargs['libtypechart'] = Pie(libtype.values()).legend('|'.join(libtype.keys())).size(225,125)

    kwargs['libauth']=libauth
    kwargs['libauthchart'] = Pie(libauth.values()).legend('|'.join(libauth.keys())).size(225,125)

    kwargs['collaborators']=collaborators
    kwargs['collaboratorschart']= Pie(collaborators.values()).legend('|'.join(collaborators.keys())).size(225,125)

    kwargs['liborg']=liborg
    kwargs['liborgchart']= Pie(liborg.values()).legend('|'.join(liborg.keys())).size(225,125)

    anaauth = defaultdict(int)
    resultids = Result.objects.all().values_list('result_id', flat=True)
    for resultid in resultids:
        author = Author.objects.filter(result__result_id=resultid).values_list('designation', flat=True)[0]
        anaauth[author] += 1

    kwargs['anaauth']=anaauth
    kwargs['anaauthchart']= Pie(anaauth.values()).legend('|'.join(anaauth.keys())).size(225,125)

    return render_to_response('ngsdbview/dashboard.html',kwargs, context_instance=RequestContext(request))



def ListLibraries(request):
    #gets user and the libraries the user has permission to
    [user, availlibids] = getlibraries(request)
    kwargs={}
    kwargs['title']='List of Libraries:'
    kwargs['listoflinks']=listoflinks
    kwargs['user']=user

    # for autocomplete
    kwargs['autocomlibcodes'] = constructAutocomplete('libcode', Library.objects.filter(library_id__in=availlibids).values_list('librarycode', flat=True))
    orgcodes = Organism.objects.filter(library__library_id__in=availlibids).values_list('organismcode', flat=True)
    kwargs['autocomorgcodes'] = constructAutocomplete('organismcode', list(set(orgcodes)))
    authors = Author.objects.filter(library__library_id__in=availlibids).values_list('designation', flat=True)
    kwargs['autocomdesignation'] = constructAutocomplete('authordesignation', list(set(authors)))

    # Default display
    availlibs = Library.objects.filter(library_id__in=availlibids)
    kwargs['availlibs']=availlibs

    # filter based on user's input via form
    if request.method == 'POST':
        form = ListLibForm(request.POST) #bound form
        if form.is_valid():
            if request.POST.get('organismcode'):
                availlibs = availlibs.filter(organism__organismcode=form.cleaned_data['organismcode'])
            if request.POST.get('authordesignation'):
                availlibs = availlibs.filter(author__designation=form.cleaned_data['authordesignation'])
            if request.POST.get('libcode'):
                availlibs = availlibs.filter(librarycode=form.cleaned_data['libcode'])
            kwargs['form']=form
            kwargs['availlibs']=availlibs

        else:
            kwargs['form']=form
    else:
        form = ListLibForm() #unbound form
        kwargs['form']=form

    return render_to_response('ngsdbview/list_libraries.html',kwargs, context_instance=RequestContext(request))
    #return render_to_response('ngsdbview/list_librariestwo.html',kwargs, context_instance=RequestContext(request))

def ListAnalyses(request):
    '''lists analysis from ngsdb'''
    #gets user and the libraries the user has permission to
    [user, availlibids] = getlibraries(request)

    kwargs={}
    kwargs['title']='List of Analyses:'
    kwargs['listoflinks']=listoflinks
    kwargs['user']=user

    # for autocomplete
    kwargs['autocomlibcodes'] = constructAutocomplete('libcode', Library.objects.filter(library_id__in=availlibids).values_list('librarycode', flat=True))
    orgcodes = Organism.objects.filter(library__library_id__in=availlibids).values_list('organismcode', flat=True)
    kwargs['autocomorgcodes'] = constructAutocomplete('organismcode', list(set(orgcodes)))
    authors = Author.objects.filter(library__library_id__in=availlibids).values_list('designation', flat=True)
    kwargs["autocomdesignation"] = constructAutocomplete('authordesignation', list(set(authors)))

    availres = Result.objects.filter(libraries__library_id__in=availlibids)
    kwargs['availres']=availres


    if request.method == 'POST':
        form = ListLibForm(request.POST) #bound form
        if form.is_valid():
            if request.POST.get('organismcode'):
                availres = availres.filter(libraries__organism__organismcode=form.cleaned_data['organismcode'])
            if request.POST.get('authordesignation'):
                availres = availres.filter(libraries__author__designation=form.cleaned_data['authordesignation'])
            if request.POST.get('libcode'):
                availres = availres.filter(libraries__librarycode=form.cleaned_data['libcode'])
            kwargs['form']=form
            kwargs['availres']=availres

        else:
            kwargs['form']=form
            print "not valid"
    else:
        form = ListLibForm() #unbound form
        kwargs['form']=form

    return render_to_response('ngsdbview/list_analyses.html',kwargs, context_instance=RequestContext(request))


def ListExperiments(request):
    '''
        Lists experiments and the libraries grouped under them
    '''
    [user, availlibids] = getlibraries(request)
    print user
    print availlibids
    kwargs={}
    kwargs['title']='List of Experiments:'
    kwargs['listoflinks']=listoflinks
    kwargs['user']=user
    # for autocomplete
    kwargs['autocomexpcodes'] = constructAutocomplete('expts', Experiment.objects.filter(libraries__librarycode__in=availlibids).values_list('name', flat=True))

    expts = {}
    allexp = Experiment.objects.all()
    for exp in allexp:
        expname = exp.name
        expts[expname] = Library.objects.filter(experiment__name=expname)

    kwargs['expts']=expts

    return render_to_response('ngsdbview/list_experiments.html',kwargs, context_instance=RequestContext(request))


def GetAlignStats(request):
    '''
        Gets and displays alignment statistics of selected libraries
    '''
    [user, availlibids] = getlibraries(request)
    kwargs={}
    kwargs['title']='Alignment Statistics:'
    kwargs['listoflinks']=listoflinks
    kwargs['user']=user

    # for autocomplete lib codes
    availlibcodes = Library.objects.filter(library_id__in=availlibids).values_list('librarycode', flat=True)
    autoclibcodes = constructAutocomplete('libcode', availlibcodes)
    kwargs['autoclibcodes'] = autoclibcodes

    if request.method == 'POST':
        form = GetAlignStatsForm(request.POST) #bound form
        if form.is_valid() and 'libcode_genome_version' in request.POST:
        #alignstat table, chart
            libcode_genome_versions = request.POST.getlist('libcode_genome_version')

            alignstatdics = {}
            alignstatpics = {}
            alignstatpercall = {}
            for libcode_genome_version in libcode_genome_versions:
                libcode_genome_version_list = libcode_genome_version.split('_')
                libcode = libcode_genome_version_list[0]
                resid = GetResidForLibcodeGenomeVersion(request, libcode, libcode_genome_version_list[1], libcode_genome_version_list[2])
                alignstatdics[libcode_genome_version] = CreateAlignstat(request, libcode, resid, 'data')
                alignstatpics[libcode_genome_version] = CreateAlignstat(request, libcode, resid, 'stackbarchart')
                alignstatpercall[libcode_genome_version] = CreateAlignstat(request, libcode, resid, 'alignperc')

            alignstatdicshori = defaultdict(lambda: defaultdict(int))
            for libcode_genome_version, alignstat in alignstatdics.items():
                alignstatdicshori['Library Code & Genome'][libcode_genome_version]=libcode_genome_version
                for rowtitle, value in alignstat.items():
                    alignstatdicshori[rowtitle][libcode_genome_version]=value

            kwargs['alignstatdicshori']= alignstatdicshori
            kwargs['roworder'] = ['Library Code & Genome', 'Original library size', 'Considered for Alignment', 'Uniquely aligned', 'Non-Uniquely aligned', 'Total Aligned Reads', 'Unaligned Reads', 'Total Aligned in Percentage', 'Unaligned in Percentage']

            print alignstatdicshori
            for libcode_genome_version, valuedic in alignstatdicshori.items():
                print libcode_genome_version
                for code, data in valuedic.items():
                    print code
                    print data


            #create align stat percentages
            alignstatperc = [[],[],[]]
            keys = []
            for key,value in alignstatpercall.items():
                keys.append(key)
                alignstatperc[0].append(value[0])
                alignstatperc[1].append(value[1])
                alignstatperc[2].append(value[2])

            #create vertical bar chart
            verticalbarchart = HorizontalBarStack([alignstatperc[0], alignstatperc[1], alignstatperc[2]]).color('4d89f9', 'c6d9fd', 'ffcc99').encoding('text').label("1", "1", "1", "1", "1", "1", "1", "1")
            width = 75 * len(keys)
            verticalbarchart.legend('Uniquely Aligned', 'NonUniquely Aligned', 'Not Aligned').axes('y').size(width,500)
            kwargs['alignstatdics']=alignstatdics
            kwargs['alignstatpics']= verticalbarchart

    else:
        form = GetAlignStatsForm() #unbound form
        kwargs['form']=form
        genomelibcodemap = GroupLibcodesByGenome(request, availlibcodes)
        kwargs['availlibcodes']=availlibcodes
        kwargs['genomelibcodemap']=genomelibcodemap

    return render_to_response('ngsdbview/get_align_stats.html',kwargs, context_instance=RequestContext(request))


def GetResultsForGene(request):
    '''
        Get results for one single gene from multiple libraries
    '''
    #gets user and the libraries the user has permission to
    [user, availlibids] = getlibraries(request)
    kwargs={}
    kwargs['title']='Query a Gene:'
    kwargs['listoflinks']=listoflinks
    kwargs['user']=user

    if request.method == 'POST':
        form = GetResultsForGeneForm(request.POST) #bound form
        if form.is_valid():
            if 'resid' in request.POST:
                geneid = form.cleaned_data['geneid']
                resids= request.POST.getlist('resid')
                allres =  Result.objects.filter(result_id__in=resids)
                slsiteobjs = Resultslsite.objects.filter(result__in=resids).filter(geneid=geneid)
                slsreadcount= getReadcountsForGeneResids(request, geneid, resids)

                libcodes = {}
                for res in allres:
                    x = Library.objects.filter(result__result_id=res.result_id).values_list('librarycode', flat=True)[0]
                    x.encode('ascii','ignore')
                    libcodes[str(res.result_id)] = x

                # ugly. This will miss if there are more than one lib involved in making one res
                interval = {}
                for resid in slsreadcount:
                    for pos in slsreadcount[resid]:
                        int = getIntervalsForGeneResid(request, geneid, resid, pos)
                        if int != "NA":
                            interval[pos]=int
                print interval
                # get ordered list of positions (using just first of resids)
                ordposlist =  sorted(slsreadcount[slsreadcount.keys()[0]].keys())

                majorsitepos = {}
                slsiteobjs = slsiteobjs.filter(rank=1)
                for slsiteobj in slsiteobjs:
                    majorsitepos[slsiteobj.result_id] = slsiteobj.position
                print majorsitepos
                kwargs['majorsitepos']=majorsitepos
                kwargs['allres']=allres
                kwargs['geneid']=geneid
                kwargs['slsiteobjs']=slsiteobjs
                kwargs['slsreadcount']=slsreadcount
                kwargs['interval']=interval
                kwargs['ordposlist']=ordposlist
                kwargs['libcodes']=libcodes
                kwargs['title']='Results for a Gene:'

            elif 'geneid' in request.POST:
                geneid = form.cleaned_data['geneid']
                allres = Result.objects.filter(resultslgene__geneid=geneid).filter(libraries__library_id__in=availlibids)
                kwargs['allres']=allres
                kwargs['geneid']=geneid

        else:
            kwargs['form']=form

    else:
        form = GetResultsForGeneForm() #unbound form
        kwargs['form']=form

    return render_to_response('ngsdbview/get_results_for_gene.html',kwargs, context_instance=RequestContext(request))

def GetResultsForMultiGenesMultiLib(request):
    '''
        Get results for multiple genes from multiple libraries
    '''
    [user, availlibids] = getlibraries(request)
    kwargs={}
    kwargs['title']='Query set of Libraries:'
    kwargs['listoflinks']=listoflinks
    kwargs['user']=user

    # for autocomplete lib codes
    availlibcodes = Library.objects.filter(library_id__in=availlibids).values_list('librarycode', flat=True)
    autoclibcodes = constructAutocomplete('libcode',availlibcodes)
    kwargs['autoclibcodes'] = autoclibcodes

    if request.method == 'POST':
        form = GetResultsForMultiGenesMultiLibForm(request.POST) #bound form
        if form.is_valid():
            resids = []
            for key, value in request.POST.items():
                if 'radio_resid' in key:
                    resids.append(value)
            # if single result for each of the libraries are selected
            if 'formlevel' in request.POST:
                libcodes = request.POST.getlist('libcodes')
                geneidbox = form.cleaned_data['geneidbox']
                geneids = string2list(request, geneidbox)
                allgenes = Resultslsite.objects.filter(result__in=resids).filter(geneid__in=geneids).order_by('geneid','rank')

                rank = form.cleaned_data['rank']
                if rank != 0:
                    allgenes = allgenes.filter(rank=rank)

                # readcount data for the table
                finalcount = {}
                for geneid in geneids:
                    resset = allgenes.filter(geneid=geneid)
                    finalcount[geneid] = resset.values_list('readcount', flat=True)
                kwargs['finalcount'] = finalcount

                # header data for table
                headerLib=[]
                headerGen=[]
                residsforheader =resset.values_list('result', flat=True)
                for resid in residsforheader:
                    headerLib.append(GetLibcodesForResid(request, resid)[0])
                    headerGen.append(GetGenomeVersionForResid(request, resid))
                kwargs['headerLib'] = headerLib
                kwargs['headerGen'] = headerGen

                #get list of geneids for tritryplink in comma separated string form
                kwargs['geneidsfortritryp'] = ','.join(geneids)
                kwargs['libcodes'] = libcodes
                kwargs['rank'] = rank

            # only geneids are filled out; selection of result set yet to be presented to the user
            elif 'geneidbox' in request.POST:
                libcodes = request.POST.getlist('libcodes')

                analysisdic = {}
                for libcode in libcodes:
                    analysisdic[libcode] = Result.objects.filter(libraries__librarycode=libcode).filter(libraries__library_id__in=availlibids)
                kwargs['analysisdic'] = analysisdic
                kwargs['form']=form
        else:
            kwargs['form'] = form
    else:
        form = GetResultsForMultiGenesMultiLibForm() #unbound form
        kwargs['form']=form
        kwargs['availlibcodes']=availlibcodes
    return render_to_response('ngsdbview/get_results_for_multigenes_multilibs.html',kwargs, context_instance=RequestContext(request))

def GetResultsForMultiGenes(request):
    '''
        Get results for multiple genes from single library
    '''
    [user, availlibids] = getlibraries(request)
    kwargs={}
    kwargs['title']='Query a Library:'
    kwargs['listoflinks']=listoflinks
    kwargs['user']=user

    # for autocomplete lib codes
    availlibcodes = Library.objects.filter(library_id__in=availlibids).values_list('librarycode', flat=True)
    autoclibcodes = constructAutocomplete('libcode',availlibcodes)
    kwargs['autoclibcodes'] = autoclibcodes


    if request.method == 'POST':
        form = GetResultsForMultiGenesForm(request.POST) #bound form
        if form.is_valid():
            if 'resid' in request.POST:
                resid= request.POST.get('resid')
                rank = form.cleaned_data['rank']
                libcode = form.cleaned_data['libcode']
                geneidbox = form.cleaned_data['geneidbox']
                geneids = string2list(request, geneidbox)
                allgenes = Resultslsite.objects.filter(result=resid).filter(geneid__in=geneids).order_by('geneid','rank')
                if rank != 0:
                    allgenes = allgenes.filter(rank=rank)

                kwargs['allgenes']=allgenes
                kwargs['form']=form
                kwargs['allres'] =  Result.objects.filter(result_id__in=resid)
                kwargs['libcode'] = libcode
                kwargs['rank'] = rank
                kwargs['resid'] = resid

                #get list of geneids for tritryplink in comma separated string form
                kwargs['geneidsfortritryp']=','.join(geneids)


            elif 'libcode' in request.POST:
                libcode = form.cleaned_data['libcode']
                allres = Result.objects.filter(libraries__librarycode=libcode).filter(libraries__library_id__in=availlibids)
                kwargs['allres'] = allres
                kwargs['form']=form
        else:
            kwargs['form'] = form
    else:
        form = GetResultsForMultiGenesForm() #unbound form
        kwargs['form']=form
    return render_to_response('ngsdbview/get_results_for_multigenes.html',kwargs, context_instance=RequestContext(request))

def GetResultsForLibrary(request):
    """
     gets user and the libraries the user has permission to
     """
    [user, availlibids] = getlibraries(request)
    kwargs={}
    kwargs['title']='Query a Library:'
    kwargs['listoflinks']=listoflinks
    kwargs['user']=user

    # for autocomplete lib codes
    availlibcodes = Library.objects.filter(library_id__in=availlibids).values_list('librarycode', flat=True)
    somejs = constructAutocomplete('libcode',availlibcodes)
    kwargs['somejs'] = somejs

    if request.method == 'POST':
        form = GetResultsForLibraryForm(request.POST) #bound form
        if form.is_valid():
            if 'resid' in request.POST:
                libcode = form.cleaned_data['libcode']
                resid= request.POST.get('resid')
                minreadcount =  form.cleaned_data['minreadcount']
                datatype = form.cleaned_data['datatype']
                outputobjs = []
                if datatype == 'gene':
                    outputobjs = Resultslgene.objects.filter(result__result_id=resid).filter(sensereadcount__gte=minreadcount)
                if datatype == 'site':
                    outputobjs = Resultslsite.objects.filter(result__result_id=resid).filter(readcount__gte=minreadcount)
                if datatype == 'raw':
                    outputobjs = Resultraw.objects.filter(result__result_id=resid).filter(totalcount__gte=minreadcount)
                allres =  Result.objects.filter(result_id__in=resid)

                #get list of geneids for tritryplink in comma separated string form
                if datatype != 'raw':
                    geneids = outputobjs.values_list('geneid', flat=True)
                    kwargs['geneidsfortritryp']=','.join(geneids)
                    kwargs['geneids']=geneids

                #alignstat table, chart
                alinstatpiechart= CreateAlignstat(request, libcode, resid, 'chart')
                alignstatdic = CreateAlignstat(request, libcode, resid, 'data')

                kwargs['allres']=allres
                #kwargs['libcode']=libcode
                kwargs['resid'] = resid
                #kwargs['minreadcount'] = minreadcount
                kwargs['datatype'] = datatype
                kwargs['outputobjs'] = outputobjs
                kwargs['form']=form
                kwargs['alinstatpiechart']=alinstatpiechart
                kwargs['alignstatdic']=alignstatdic
                kwargs['title']='Results for a Library:'


            elif 'libcode' in request.POST:
                libcode = form.cleaned_data['libcode']
                allres = Result.objects.filter(libraries__librarycode=libcode).filter(libraries__library_id__in=availlibids)
                kwargs['allres'] = allres
                kwargs['form']=form

        else:
            kwargs['form']=form
    else:
        form = GetResultsForLibraryForm() #unbound form
        kwargs['form']=form
    return render_to_response('ngsdbview/get_results_for_lib.html',kwargs, context_instance=RequestContext(request))

def GetSitesForLibrary(request):
    """
    Gets a site of a rank for all the genes in a lib
    """
    [user, availlibids] = getlibraries(request)
    kwargs={}
    kwargs['title']='Query a Library:'
    kwargs['listoflinks']=listoflinks
    kwargs['user']=user

    # for autocomplete lib codes
    availlibcodes = Library.objects.filter(library_id__in=availlibids).values_list('librarycode', flat=True)
    autoclibcodes = constructAutocomplete('libcode',availlibcodes)
    kwargs['autoclibcodes'] = autoclibcodes


    if request.method == 'POST':
        form = GetSitesForLibraryForm(request.POST) #bound form
        if form.is_valid():
            if 'resid' in request.POST:
                rank = form.cleaned_data['rank']
                libcode = form.cleaned_data['libcode']
                minreadcount = form.cleaned_data['minreadcount']
                resid= request.POST.get('resid')
                allgenes = Resultslsite.objects.filter(result=resid).filter(rank=rank).filter(readcount__gte=minreadcount)
                kwargs['allgenes']=allgenes
                kwargs['allres'] =  Result.objects.filter(result_id__in=resid)
                kwargs['form']=form
                #alignstat table, chart
                alinstatpiechart= CreateAlignstat(request, libcode, resid, 'chart')
                alignstatdic = CreateAlignstat(request, libcode, resid, 'data')
                kwargs['alignstatdic']=alignstatdic
                kwargs['alinstatpiechart']=alinstatpiechart
                kwargs['minreadcount']=minreadcount
                #get list of geneids for tritryplink in comma separated string form
                geneids = allgenes.values_list('geneid', flat=True)
                kwargs['geneidsfortritryp']=','.join(geneids)


            elif 'libcode' in request.POST:
                libcode = form.cleaned_data['libcode']
                allres = Result.objects.filter(libraries__librarycode=libcode).filter(libraries__library_id__in=availlibids)
                kwargs['allres'] = allres
                kwargs['form']=form
        else:
            kwargs['form'] = form
    else:
        form = GetSitesForLibraryForm() #unbound form
        kwargs['form']=form

    return render_to_response('ngsdbview/get_sites_forlib.html',kwargs, context_instance=RequestContext(request))

def GetSitecountMajorpcForLibs(request):
    libs=['AH038','AH039']#, 'AH040','AH041','AH042','AH094','AH095']
    genomeid = "1"
    minreadcount = "10"

    # Generate GeneDic from Fetures; Generate resultid dic from libcodes
    genedic = GetGeneDesForGenomeid(request, genomeid)
    residdic={}
    for lib in libs:
        residdic[lib]=GetResidForLibcodeGenomeid(request, lib, genomeid)

    # Declare vars to hold master data
    outputdata = {}
    seengenes = {}
    for geneid in genedic:
        outputdata[geneid]={}

    # Iterate libs for sensesite count from gene table
    for lib in libs:
        resgenedic = {}
        resgeneobjs = Resultslgene.objects.filter(result=residdic[lib])
        for resgene in resgeneobjs:
            resgenedic[resgene.geneid] = resgene.sensesitecount
        for geneid in genedic:
            if geneid in resgenedic:
                outputdata[geneid][lib]=[resgenedic[geneid]]
            else:
                outputdata[geneid][lib]=["0"]


    # Iterate libs for sensesite count from slsite table with readcount limit
    for lib in libs:
        ressiteobjs2 = Resultslsite.objects.filter(result=residdic[lib]).filter(readstrand='SENSE').filter(readcount__gte="0")

        sitecountdic = defaultdict(int)
        for ressite in ressiteobjs2:
            sitecountdic[ressite.geneid] += 1
        for geneid in genedic:
            if geneid in sitecountdic:
                outputdata[geneid][lib].append(sitecountdic[geneid])
            else:
                outputdata[geneid][lib].append("0")


    # Iterate libs for sensesite count from slsite table with readcount limit
    for lib in libs:
        ressiteobjs2 = Resultslsite.objects.filter(result=residdic[lib]).filter(readstrand='SENSE').filter(readcount__gte=minreadcount)

        sitecountdic = defaultdict(int)
        for ressite in ressiteobjs2:
            sitecountdic[ressite.geneid] += 1
        for geneid in genedic:
            if geneid in sitecountdic:
                outputdata[geneid][lib].append(sitecountdic[geneid])
            else:
                outputdata[geneid][lib].append("0")


    # Iterate libs for slpercent  for site with a rank number from slsite table with readcount limit
    for lib in libs:
        ressitedic = {}
        ressiteobjs = Resultslsite.objects.filter(result=residdic[lib]).filter(rank=1)
        for ressite in ressiteobjs:
            ressitedic[ressite.geneid] = ressite.slpercent
        for geneid in genedic:
            if geneid in ressitedic:
                outputdata[geneid][lib].append(ressitedic[geneid])
            else:
                outputdata[geneid][lib].append("0")

    # Iterate libs for slpercent  for site with a rank number from slsite table with readcount limit
    for lib in libs:
        ressitedic = {}
        ressiteobjs = Resultslsite.objects.filter(result=residdic[lib]).filter(rank=1).filter(readcount__gte=minreadcount)
        for ressite in ressiteobjs:
            ressitedic[ressite.geneid] = ressite.slpercent
        for geneid in genedic:
            if geneid in ressitedic:
                outputdata[geneid][lib].append(ressitedic[geneid])
            else:
                outputdata[geneid][lib].append("0")



    return render_to_response('ngsdbview/get_sitecount_majorpc_forlibs.html',
            {'outputdata': outputdata,
             'genedic': genedic,
             'residdic': residdic,
             }, context_instance=RequestContext(request))







