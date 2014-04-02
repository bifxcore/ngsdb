# Create your views here.
from django.shortcuts import render
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from samples.tables import *

def author(request):
    table = AuthorTable(Author.objects.all())
    RequestConfig(request, paginate={"per_page": 25}).configure(table)

    return render(request, "samples/author.html", {"author": table})



def librarylist(request):
    table = LibraryTable(Library.objects.all())
    RequestConfig(request).configure(table)

    return render(request, "samples/librarylist.html", {"librarylist": table})