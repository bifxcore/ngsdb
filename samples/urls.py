from django.conf.urls import *

urlpatterns = patterns('',


    url(r'^authors/$','samples.views.author'),
    url(r'^reservecodes/$', 'samples.views.ReserveCode'),

    url(r'^samples/', 'samples.views.ListSamples'),
    url(r'^viewsample/(?P<sampleid>.+)/', 'samples.views.ViewSample'),
    url(r'^libraries/', 'samples.views.ListLibraries'),
    url(r'^viewlibrary/(?P<librarycode>.+)/', 'samples.views.ViewLibrary'),

    url(r'^bioprojects/', 'samples.views.ListBioprojects'),
    url(r'^bioprojectstable2/', 'samples.views.ListBioprojectsTable2'),

    )