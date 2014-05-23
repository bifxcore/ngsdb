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
    parser = argparse.ArgumentParser(description='Uploads RiboProfiling count data into Ngsdb03+.')
    parser.add_argument('--inputfile', required=True, help='the inputfile that was piped into runRiboProfseqPipeline.pl during analysis')
    parser.add_argument('--ymlfile', required=True, help='the ymlfile that was outputed after runRiboProfseqPipeline.pl during analysis')
    parser.add_argument('--rawreadcountfile',  required=True, help='the file with raw count data. \nShould have two columns, tab separated\n.<geneid>\t<raw count>\n')
    parser.add_argument('--librarycode',  required=True, help='the inputfile that was piped into runRiboProfseqPipeline.pl during analysis', type=str)
    parser.add_argument('--featuretype',  required=True, help='feature type for the count data.', choices= ['CDS', '5UTR', '3UTR', 'ATG'], default="CDS", type=str)
    parser.add_argument('--librarysize', help='Size (total read counts) of the library', type=int)
    parser.add_argument('--version', '-v',  action='version', version='%(prog)s 1.0')
    args = parser.parse_args()
    return args

def hasify_input_file(inputfile):
    # Keys for input file # parse input file
    inputkeys = ['basepath', 'fastqpath', 'organism', 'lifestage', 'phenotype', 'downloaddate', 'flowcell', 'samplenotes', 'librarytype', 'protocol', 'collab_firstname', 'collab_lastname', 'author', 'analysisauthor', 'genome', 'genomeversion', 'genomesource','analysisnotes']
    print inputkeys
    f = open(inputfile, 'r')
    csvlines = f.read().splitlines()

    # zip them to a dict
    inputdic = dict(zip(inputkeys, csvlines))
    print(inputdic)
    return inputdic

def load_results(inputdic, newlibobjid):
    newresobj = Result()
    newresobj.genome = Genome.objects.get(organism__organismcode=inputdic['genome'], version=inputdic['genomeversion'], source='SBRI')
    newresobj.author = Author.objects.get(designation=inputdic['analysisauthor'])
    newresobj.analysispath = inputdic['basepath']
    newresobj.notes = inputdic['analysisnotes']
    newresobj.is_obsolete = False
    newresobj.is_current = True
    newresobj.save()
    newresobjid = newresobj.result_id


    # Now save the link table in many-to-many realtionship
    newlibobj = ngsdbviewlibrary.objects.get(library_id=newlibobjid)
    newresobj.libraries.add(newlibobj)

    return newresobjid

def load_library(libcode, inputdic, librarysize):
    # create a new object for ngsdbview.Library model
    newlibobj = ngsdbviewlibrary(fastqpath=inputdic['fastqpath'], fastqname=basename(inputdic['fastqpath']), fastqalias=basename(inputdic['fastqpath']))

    # obtain data from samples library
    libobj = sampleslibrary.objects.filter(library_code=libcode)
    if len(libobj) > 1:
        print "Multiple libraries with same Library code"
        die()
    elif len(libobj) == 1:
        libobj = libobj[0]


    # add protocol from ngsdbview. THis needs to be resolved.
    # right now there is a duplicate table in samples too
    # and entries need to be redundant
    newlibobj.protocol = ngsdbviewprotocol.objects.get(name='RiboProf_BJ_01')


    newlibobj.librarysize = librarysize
    # obtain remaining values from samples.library model (libobj/sampleslibrary)
    newlibobj.librarycode = libobj.library_code
    newlibobj.author = libobj.author
    newlibobj.collaborator = libobj.collaborator
    newlibobj.organism = libobj.organism
    newlibobj.lifestage = libobj.lifestage
    newlibobj.phenotype = libobj.phenotype
    newlibobj.librarytype = libobj.librarytype
    newlibobj.flowcell = libobj.flowcell_number
    newlibobj.downloaddate = libobj.sequence_downloaded_on
    newlibobj.notes = libobj.sample_notes

    newlibobj.save()
    newlibobjid = newlibobj.library_id

    return newlibobjid

def load_countdata(newresobjid, featuretype, rawreadcountfile):
    #read the count data file
    data = open(rawreadcountfile, 'r')
    for datarow in data.readlines():
        print datarow
        data = datarow.split("\t")
        newcountobj = Resultsriboprof(geneid=data[0], featuretype=featuretype, counts_raw=data[1], counts_normalized=0)
        newcountobj.result = Result.objects.get(result_id=newresobjid)
        newcountobj.save()


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
libcode = args.librarycode
inputfile = args.inputfile
ymlfile = args.ymlfile
featuretype = args.featuretype
rawreadcountfile = args.rawreadcountfile
librarysize = args.librarysize
libobj = ""




#hasify the input file
print "Step 1: Reading in input file...."
inputdic = hasify_input_file(inputfile)

# Work on loading library first.
#check if the lib already exists; decide to continiue or abort
newlibobjid = ""
l = ngsdbviewlibrary.objects.filter(librarycode=libcode)
if len(l) == 1:
    print "This library already exits\n"
    newlibobjid = ngsdbviewlibrary.objects.filter(librarycode=libcode)[0].library_id
    print "Current id for this library is", newlibobjid
    #procede = input("Procede loading results/analysis info?[y|n]")
    #if procede == 'n':
    #    die()
    #else:
    #    pass
elif len(l) > 1:
    print "Multiple libraries exists with the same name. Aborting......"
    die()
else:
    print "No Library exists with this id, continuing to load....."
    newlibobjid = load_library(libcode, inputdic, librarysize)



# Now that we have the library loaded. procede to load result table
newresobjid = ""
r = Result.objects.filter(libraries__librarycode=libcode)
if len(r) == 1:
    rid = r[0].result_id
    print "This Analysis/Result already exits. Result id:", rid
    newresobjid = rid
elif len(l) > 1:
    print "Multiple analysis/results exists for this library. Aborting......"
    die()
else:
    print "No Analysis/Results exists for this library, continuing to load....."
    newresobjid = load_results(inputdic, newlibobjid)


# Now that we have loaded all the requiremnts, procede to load actual data
# into Resultriboprof table
load_countdata(newresobjid, featuretype, rawreadcountfile)


# Now load Resultprop, Aanalysis and Analysisprop
populate_resultprop(newresobjid, ymlfile)
populate_analysis(newresobjid, ymlfile)
