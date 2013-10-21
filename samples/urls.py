from django.conf.urls import *

urlpatterns = patterns('',

    # Wen-Wai's views
    url(r'^authors/$','samples.views.author'),
    url(r'^librarylist/$', 'samples.views.librarylist')
    )