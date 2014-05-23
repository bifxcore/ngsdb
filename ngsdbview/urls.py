from django.conf.urls import *
from models import Library

table = Library.objects.all()

urlpatterns = patterns('',

    # Wen-Wai's views
    url(r'^ngsdbview_library/$','ngsdbview.views.ViewLib'),
    url(r'^ngsdbview_result/$','ngsdbview.views.ViewResult'),
    url(r'^list_analysis_steps/(?P<result_id>.+)/','ngsdbview.views.ListAnalysisSteps'),
    url(r'^contact/$', 'ngsdbview.views.Contact'),
    url(r'^aboutus/$', 'ngsdbview.views.About'),


    # Gowthaman's views
    url(r'^$', 'ngsdbview.views02.Dashboard'),
    url(r'^dashboard/','ngsdbview.views02.Dashboard'),
    url(r'^listlibraries/','ngsdbview.views02.ListLibraries'),
    url(r'^listanalyses/','ngsdbview.views02.ListAnalyses'),
    url(r'^listexperiments/','ngsdbview.views02.ListExperiments'),
    url(r'^get_results_for_gene/','ngsdbview.views02.GetResultsForGene'),
    url(r'^query_multigenes/','ngsdbview.views02.GetResultsForMultiGenes'),
    url(r'^query_multigenes_multilibs/','ngsdbview.views02.GetResultsForMultiGenesMultiLib'),
    url(r'^get_results_for_library/','ngsdbview.views02.GetResultsForLibrary'),
    url(r'^Get_sites_forlib/','ngsdbview.views02.GetSitesForLibrary'),
    url(r'^get_sitecount_majorpc_forlibs/','ngsdbview.views02.GetSitecountMajorpcForLibs'),
    url(r'^pair_libraries/','ngsdbview.views02.PairLibraries'),
    url(r'^alignstats/', 'ngsdbview.views02.GetAlignStats'),

)
