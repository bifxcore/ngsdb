# Create your views here.
from django.shortcuts import render
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from samples.tables import *
from ngsdbview.viewtools import *
from samples.models import *
from django import forms

def author(request):
    table = AuthorTable(Author.objects.all())
    RequestConfig(request, paginate={"per_page": 25}).configure(table)

    return render(request, "samples/author.html", {"author": table})



def librarylist(request):
    table = LibraryTable(Library.objects.all())
    RequestConfig(request).configure(table)

    return render(request, "samples/librarylist.html", {"librarylist": table})


class ListLibForm(forms.Form):
    """ form for searching libraries loaded into ngsdb """
    authordesignation = forms.CharField(max_length=20, label='Author Initials', required=False)
    organismcode = forms.CharField(max_length=20, label='Organism Code', required=False)
    libcode = forms.CharField(max_length=20, label='Library Code', required=False)


def ListLibraries(request, libtype, analysis_status):
    #gets user and the libraries the user has permission to
    [user, availlibids] = getlibraries(request)
    kwargs={}
    kwargs['title']='List of Libraries:'
    kwargs['listoflinks']=listoflinks
    kwargs['user']=user

    # # for autocomplete
    # kwargs['autocomlibcodes'] = constructAutocomplete('libcode', Library.objects.filter(library_id__in=availlibids).values_list('librarycode', flat=True))
    # orgcodes = Organism.objects.filter(library__library_id__in=availlibids).values_list('organismcode', flat=True)
    # kwargs['autocomorgcodes'] = constructAutocomplete('organismcode', list(set(orgcodes)))
    # authors = Author.objects.filter(library__library_id__in=availlibids).values_list('designation', flat=True)
    # kwargs['autocomdesignation'] = constructAutocomplete('authordesignation', list(set(authors)))

    # Default display
    # Get all available libs
    availlibs = Library.objects.filter(id__in=availlibids)
    # Filter for libtype
    if libtype != 'all':
        availlibs = availlibs.filter(librarytype__type=libtype)

    # Filter for analysis_status
    if analysis_status == 'analysed':
        pass
    elif analysis_status == 'all':
        pass
    else:
        pass
    #todo: add the code once EVERYTHING is linked to Samples.Library
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

