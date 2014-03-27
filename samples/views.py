# Create your views here.
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from samples.models import *
from samples.tables import *


def author(request):
    kwargs = {}
    table = AuthorTable(Author.objects.all())
    RequestConfig(request, paginate={"per_page": 25}).configure(table)

    kwargs['author'] = table
    return render_to_response('samples/author.html', kwargs, context_instance=RequestContext(request))



def librarylist(request):
    table = LibraryTable(Library.objects.all())
    RequestConfig(request).configure(table)

    return render(request, "samples/librarylist.html", {"librarylist": table})