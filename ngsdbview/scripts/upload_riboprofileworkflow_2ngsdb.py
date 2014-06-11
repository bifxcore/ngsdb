###################################################################
# set up for making Django environment & imports
###################################################################
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from django.core.management import setup_environ
os.environ['DJANGO_SETTINGS_MODULE'] = 'ngsdb03.settings.gowthamanlaptop'
from ngsdb03 import settings
setup_environ(settings)

from os.path import basename
from samples.models import Library as sampleslibrary
from ngsdbview.models import Library as ngsdbviewlibrary, Protocol as ngsdbviewprotocol
from ngsdbview.models import Result, Author, Genome, Resultsriboprof, Analysis, Analysisprop, Analysistype, Software, Cvterm
import yaml
####################################################################
#
# Functions
#
####################################################################
def argparse():
    import argparse
    parser = argparse.ArgumentParser(description='Uploads RiboProfiling workflow summary into Ngsdb03+.')
    parser.add_argument('--ymlfile', required=True, help='the ymlfile that was outputed after runRiboProfseqPipeline.pl during analysis')
    parser.add_argument('--resultid', required=True, help='result id for which workflow data to be loaded')
    parser.add_argument('--version', '-v',  action='version', version='%(prog)s 1.0')
    args = parser.parse_args()
    return args


def populate_analysis(resultid, ymlfile):
    ymlstream = file(ymlfile, "r")
    ymldata = yaml.load(ymlstream)
    print "Populating analysis log\n"
    for analysis_step in ymldata['analysis']:
        print analysis_step
        if ymldata['analysis'][analysis_step]['performed']:
            # load analysis table
            # gene analysis, type and software ids
            newanalysisobj = Analysis(result=Result.objects.get(result_id=resultid), ordinal=ymldata['analysis'][analysis_step]['ordinal'], notes="NA")
            newanalysisobj.analysistype = Analysistype.objects.get(type=analysis_step)
            newanalysisobj.software = Software.objects.get(name=ymldata['analysis'][analysis_step]['program'], version=ymldata['analysis'][analysis_step]['program_version'])
            print(newanalysisobj)
            newanalysisobj.save()
            print(newanalysisobj)
            newanalysisobjid = newanalysisobj.analysis_id

            # load analysisprop
            for cvterm in ymldata['analysis'][analysis_step]:
                newanalysispropobj = Analysisprop(analysis=Analysis.objects.get(analysis_id=newanalysisobjid))
                newanalysispropobj.cvterm = Cvterm.objects.get(name=cvterm)
                newanalysispropobj.value = ymldata['analysis'][analysis_step][cvterm]
                print(newanalysispropobj)
                newanalysispropobj.save()
                print(newanalysispropobj)
        else:
            print("not performed    ")


def populate_resultprop(resultid, ymlfile):
    print "Right now this info is not captured off of riboprof pipeline."
    pass

####################################################################
#
# main
#
####################################################################
args = argparse()
resultid = args.resultid
ymlfile = args.ymlfile
libobj = ""

populate_resultprop(resultid, ymlfile)

populate_analysis(resultid, ymlfile)
