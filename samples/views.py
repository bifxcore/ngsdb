# Create your views here.
from samples.models import *
from django.shortcuts import render

def author(request):
    return render(request, "samples/author.html", {"author": Author.objects.all()})

def librarylist(request):
    return render(request, "samples/librarylist.html", {"librarylist": Library.objects.all()})