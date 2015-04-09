# Create your views here.
from django.shortcuts import render
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from samples.tables import *
from ngsdbview.viewtools import *
from samples.models import *
from django import forms

def get_libobj_for_sample(request, samples):
    map = {}
    for sample in samples:
        libs = sample.library_set.all()
        map[sample.sampleid]=libs
    return map

def GetChoiceValueTuple(queryset, fieldname):
        values = queryset.values_list(fieldname, flat=True)
        unique_values = ['ALL']
        [unique_values.append(item) for item in values if item not in unique_values]
        choice_list = []
        for item in unique_values:
            choice_list.append(tuple([item, item]))
        return tuple(choice_list)

def author(request):
    table = AuthorTable(Author.objects.all())
    RequestConfig(request, paginate={"per_page": 25}).configure(table)

    return render(request, "samples/author.html", {"author": table})


## Samples
class ListSamplesForm(forms.Form):
    sampletype = forms.ChoiceField(choices=GetChoiceValueTuple(Sample.objects.all(), 'sampletype'))
    organism = forms.ChoiceField(choices=GetChoiceValueTuple(Organism.objects.all(), 'organismcode'))
    collaborator = forms.ChoiceField(choices=GetChoiceValueTuple(Collaborator.objects.all(), 'lastname'))

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
        form = ListSamplesForm(request.POST) #bound form
        if form.is_valid():
            sampletype = form.cleaned_data['sampletype']
            organism = form.cleaned_data['organism']
            collaboratorLN = form.cleaned_data['collaborator']

            # get experiments

            samples = Sample.objects.all()
            if sampletype != 'ALL':
                samples = samples.filter(sampletype=sampletype)
            if organism != 'ALL':
                samples = samples.filter(organism__organismcode=organism)
            if collaboratorLN != 'ALL':
                samples = samples.filter(collaborator__lastname=collaboratorLN)

            samples_RNA = samples.filter(sampletype='RNA')
            samples_DNA = samples.filter(sampletype='DNA')

            org_wise = {}
            # divide RNA samples by organism
            samples_RNA_org_wise = {}
            for sample in samples_RNA:
                samples_RNA_org_wise[sample.organism]=[]
            for orgcode in samples_RNA_org_wise:
                samples_RNA_org_wise[orgcode]=samples_RNA.filter(organism=orgcode)
            kwargs['samples_RNA_org_wise']=samples_RNA_org_wise
            org_wise['RNA'] = samples_RNA_org_wise

            # divide DNA samples by organism
            samples_DNA_org_wise = {}
            for sample in samples_DNA:
                samples_DNA_org_wise[sample.organism]=[]
            for orgcode in samples_DNA_org_wise:
                samples_DNA_org_wise[orgcode]=samples_RNA.filter(organism=orgcode)
            kwargs['samples_DNA_org_wise']=samples_DNA_org_wise
            org_wise['DNA'] = samples_DNA_org_wise

            kwargs['org_wize_samples'] = org_wise

            kwargs['sample_libraryobj_map'] = get_libobj_for_sample(request, samples)
            kwargs['samples']=samples
            kwargs['samples_RNA']=samples_RNA
            kwargs['samples_DNA']=samples_DNA

            kwargs['form']=form
        else:
            kwargs['form']=form
    else:
        form = ListSamplesForm() #un bound form
        kwargs['form']=form



    return render_to_response('samples/samples_list.html',kwargs, context_instance=RequestContext(request))

def ViewSample(request, sampleid):
    '''
    Detailed view of a sample.
    :param request: Sample code/sample id
    :return: Sample object; with libraries (objects) made from them
    '''

    kwargs = {}
    #kwargs['user']=user
    kwargs['listoflinks']=listoflinks
    kwargs['title']="Samples View"

    samples = Sample.objects.filter(sampleid=sampleid)
    kwargs['sample_libraryobj_map'] = get_libobj_for_sample(request, samples)
    kwargs['sample'] = samples[0]

    return render_to_response('samples/samples_view.html',kwargs, context_instance=RequestContext(request))


## Libraries
class ListLibrariesForm(forms.Form):
    library_type = forms.ChoiceField(choices=GetChoiceValueTuple(Librarytype.objects.all(), 'type'))
    organism = forms.ChoiceField(choices=GetChoiceValueTuple(Organism.objects.all(), 'organismcode'))
    collaborator = forms.ChoiceField(choices=GetChoiceValueTuple(Collaborator.objects.all(), 'lastname'))
    library_author = forms.ChoiceField(choices=GetChoiceValueTuple(Author.objects.all(), 'lastname'))

def ListLibraries(request):
    '''
    List all loaded Libraries. Allow exploration.
    :param request:
    :return: all Library objects; with samples made from them
    '''

    kwargs = {}
    #kwargs['user']=user
    kwargs['listoflinks']=listoflinks
    kwargs['title']="Library List"


    if request.method == 'POST':
        form = ListLibrariesForm(request.POST) #bound form
        if form.is_valid():
            librarytype = form.cleaned_data['library_type']
            organism = form.cleaned_data['organism']
            collaboratorLN = form.cleaned_data['collaborator']
            libraryauthorLN = form.cleaned_data['library_author']

            # get/filter libraries
            libs = Library.objects.all()
            if librarytype != 'ALL':
                libs = libs.filter(librarytype__type=librarytype)
            if organism != 'ALL':
                libs = libs.filter(organism__organismcode=organism)
            if collaboratorLN != 'ALL':
                libs = libs.filter(collaborator__lastname=collaboratorLN)
            if libraryauthorLN != 'ALL':
                libs = libs.filter(author__lastname=libraryauthorLN)

            kwargs['libraries_all'] = libs
            # subset libraries by type
            libraries_by_type = {}
            libraries_by_type['RNA seq'] = libs.filter(librarytype__type='fragRNA')
            libraries_by_type['DNA seq'] = libs.filter(librarytype__type='genomic')
            libraries_by_type['SL-RNA seq']=libs.filter(librarytype__type='SL')
            libraries_by_type['IP seq'] = libs.filter(librarytype__type='ChIPseq')
            libraries_by_type['polyA seq'] = libs.filter(librarytype__type='polyA')
            libraries_by_type['small-RNA seq'] = libs.filter(librarytype__type='smallRNA')
            libraries_by_type['ChIP seq'] = libs.filter(librarytype__type='ChIPChIP')
            kwargs['libraries_by_type'] = libraries_by_type

            # Send bound form
            kwargs['form'] = form

        else:
            kwargs['form'] = form
    else:
        form = ListLibrariesForm() #un bound form
        kwargs['form'] = form

    return render_to_response('samples/libraries_list.html',kwargs, context_instance=RequestContext(request))

def ViewLibrary(request, librarycode):
    '''
    Detailed view of a Library.
    :param request: Library code/Library id
    :return: Library object; with sample (objects) it derived from
    '''

    kwargs = {}
    #kwargs['user']=user
    kwargs['listoflinks']=listoflinks
    kwargs['title']="Library View"
    kwargs['library'] = Library.objects.get(library_code=librarycode)
    kwargs['all_sibling_libs'] = Library.objects.get(library_code=librarycode).sampleid.library_set.all()
    print kwargs['all_sibling_libs']

    print kwargs['library']
    return render_to_response('samples/library_view.html',kwargs, context_instance=RequestContext(request))


## Bioprojects
def ListBioprojects(request):
    """
    List all loaded bioprojects. Allow exploration.
    :param request:
    :return: all bioprojects objects;
    """

    kwargs = {}
    #kwargs['user']=user
    kwargs['listoflinks']=listoflinks
    kwargs['title']="BioProjects List"

    bioprojects = BioprojectsTable(Bioproject.objects.all())
    bioprojects.paginate(page=request.GET.get('page', 1), per_page=20)
    #RequestConfig(request).configure(bioprojects)
    kwargs['bioprojects'] = bioprojects
    return render_to_response('samples/bioproject_list.html',kwargs, context_instance=RequestContext(request))
    #return render(request, 'samples/bioproject_list.html', {'bioprojects': bioprojects})

## Bioprojects via django-table2
def ListBioprojectsTable2(request):
    """
    List all loaded bioprojects. Allow exploration.
    :param request:
    :return: all bioprojects objects;
    """

    kwargs = {}
    #kwargs['user']=user
    kwargs['listoflinks']=listoflinks
    kwargs['title']="BioProjects List"

    kwargs['bioprojects'] = Bioproject.objects.all()

    return render_to_response('samples/bioproject_list_table2.html',kwargs, context_instance=RequestContext(request))


## Reserve Sample/library codes
"""
Reserve codes for future use
view: ReserveCode
Template: samples/reservecodes.html
"""

def get_codes_by_initial(request, initial):
    '''
    :param request:
    :param initial: Author intial to be used as prefix for library/sample codes
    :return: list of codes from library, Sample and Reserved ones
    '''
    library_codes = Library.objects.filter(library_code__startswith=initial).values_list('library_code', flat=True)
    sample_codes  = Sample.objects.filter(sampleid__startswith=initial).values_list('sampleid', flat=True)
    reserved_codes = Reservedcode.objects.filter(code__startswith=initial).values_list('code', flat=True)
    all_codes = list(library_codes) + list(sample_codes) + list(reserved_codes)
    return all_codes

def get_highest_codenumber(request, code_list):
    '''
    :param request:
    :param code_list: list of library, sample codes including reserved codes
    :return: number part of highest code
    '''
    numbers = []
    for code in code_list:
        numbers.append(code[2:])
    if not numbers:
        numbers = ["0"]
    return sorted(numbers)[-1]

def code_exists(request, code):
    exist=False
    if Library.objects.filter(library_code=code).exists():
        exist=True
    if Sample.objects.filter(sampleid=code).exists():
        exist=True
    if Reservedcode.objects.filter(code=code).exists():
        exist=True
    return exist

CODETYPE_CHOICES = (('library', 'Library',), ('sample', 'Sample',))
class ReserveCodeForm(forms.Form):
    """ form for reserving library/sample codes    """
    number_of_codes = forms.IntegerField(help_text="Number of codes to reserve")
    code_type = forms.ChoiceField(widget=forms.RadioSelect, choices=CODETYPE_CHOICES)
    collaborator = forms.ModelChoiceField(queryset=Collaborator.objects.all(), empty_label="Select One", help_text="Codes will be prefixed with initials of the collaborator. Choose MySelf to prefix with your own initials.")
    initial = forms.CharField(required=False, max_length=2, help_text="Provide custom two letter initial to be used. e.g., LH.  Needed only when one DOES NOT want to use a collaborators initials.")

def ReserveCode(request):
    '''
    :param request:
    :return: Reserves the codes for the user
    '''
    [user, availlibids] = getlibraries(request)
    kwargs={}

    kwargs['title']='Reserve Code for Later use:'
    kwargs['user']=user

    # filter based on user's input via form
    if request.method == 'POST':
        form = ReserveCodeForm(request.POST) #bound form
        if form.is_valid():
            number_of_codes = form.cleaned_data['number_of_codes']
            code_type = form.cleaned_data['code_type']
            collaborator = form.cleaned_data['collaborator']
            if form.cleaned_data['initial']:
                initial = form.cleaned_data['initial'].upper()
            else:
                initial = collaborator.firstname[0].upper() + collaborator.lastname[0].upper()
            # get codons for that initial
            codesinuse = get_codes_by_initial(request, initial)
            # get the highest number among the current codes
            highest_codenumber = get_highest_codenumber(request, codesinuse)

            # Add an entry in Reserve (parent) model
            newReserve = Reserve(author=user, notes='form.cleaned_data[notes]')
            newReserve.save()
            kwargs['reserve']=newReserve

            # increment highest codenumber and generate new ones
            # save them in reservedcode model and present it to user
            next_number = int(highest_codenumber)
            reservedcodes = []
            for i in range(number_of_codes):
                next_number += 1
                next_code = initial+str("%03d" % (next_number,))
                # double check it does not exist by querying next_code against Library/Sample/Reservedcode
                exists = code_exists(request, next_code)
                if exists:
                    print "Thought, this code(%s) is novel. But seems to exist somewhere. I can't trust myself" %(next_code)
                else:
                    print next_code
                    newReservedcode = Reservedcode(reserve=newReserve, code=next_code)
                    newReservedcode.save()
                    reservedcodes.append(next_code)

            kwargs['form']=form
            kwargs['code_type']=code_type
            kwargs['reservedcodes']=reservedcodes

        else:
            kwargs['form']=form
    else:
        form = ReserveCodeForm() #unbound form
        kwargs['form']=form

    return render_to_response('samples/reservecodes.html',kwargs, context_instance=RequestContext(request))

