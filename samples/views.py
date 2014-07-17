# Create your views here.
from django.shortcuts import render
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from samples.tables import *
from ngsdbview.viewtools import *
from samples.models import *

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


def ListLibraries(request, libtype):
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
    availlibs = Library.objects.filter(id__in=availlibids)
    if libtype != 'ALL':
        availlibs = availlibs.filter(librarytype__type=libtype)

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
