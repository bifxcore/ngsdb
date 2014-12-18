#!/Users/gramasamy/virtualenv/ngsdb03/bin/python

# to execute this script from anywhere
import sys, os
sys.path.append('/Users/gramasamy/djcode/ngsdb03/')
#os.environ['DJANGO_SETTINGS_MODULE'] = 'ngsdb03.settings.gowthamanlaptop' # Not needed when evn. variable is set
from django.conf import settings

# import for the scripts actions
import time
from ngsdbview.models import Experiment,Exptsetup, Genome, Comparison, Exptfile, Compfile, Diffexpn, Tagcount
from samples.models import Library
from django.core.files import File
from django.contrib.auth.models import User
from os import path
from collections import defaultdict
from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


####################################################################
#
# Functions
#
####################################################################
def argparse():
    import argparse
    parser = argparse.ArgumentParser(description='Uploads Expression Analysis data to Experiment model and its pals.')
    parser.add_argument('--yamlfile', required=True, help='the ymlfile that was outputed after expression analysis')
    parser.add_argument('--basepath',  required=True, help='Base path for the directory which contains all the files, including yaml.\n')
    parser.add_argument('--experimentVersion',  required=True, help='version of the analysis', type=str)
    parser.add_argument('--experimentType',  required=True, help='Type of the experiment', choices= ['RNAseq', 'SpliceLeader', 'RibosomeProfiling'], default="RNAseq", type=str)
    parser.add_argument('--username', required=True, help='Name of the db user', default="gramasamy", type=str)
    parser.add_argument('--genomeOrganism', required=True, help='Reference genomes\' organism Code', default="LinJ", type=str)
    parser.add_argument('--genomeVersion', required=True, help='Version of the genome(TriTrypDB)', default="8.0", type=str)
    parser.add_argument('--debug', required=False, default=False, type=bool)
    parser.add_argument('--overwrite', required=False, help='Set this to True if existing Experiments needs to be overwritten.', default=False, type=bool)
    parser.add_argument('--version', '-v',  action='version', version='%(prog)s 1.0')
    args = parser.parse_args()
    return args

def hasify_counts(countsFile, basepath):
    countsObj = open(os.path.join(basepath, countsFile), 'r')
    headerStr = countsObj.readline()
    headers = headerStr.rstrip('\n').split("\t")
    headers.pop(0)
    countsDic = defaultdict(lambda: defaultdict(int))
    for line in countsObj:
        values = line.rstrip('\n').split("\t")
        featureID = values.pop(0)
        newDic = dict(zip(headers, values))
        for libcode, count in newDic.items():
            countsDic[libcode][featureID] = count
    return countsDic

def example():
    command = '''
    ~/djcode/ngsdb03/ngsdbview/scripts/uploadDETestResults.py --yamlfile LdBob.Nicola.RNAseq.edgeR.plus5.yml --basepath /Volumes/ngs/projects/Ldo_Purine_Nicola/vsLinJ/Expression_Analysis/LinJ.TriTrypDB8p0.CDS.union/edgeR.plus5_GENEs --experimentVersion 3.0 --experimentType RNAseq --username gramasamy --genomeOrganism LinJ --genomeVersion 8.0
    '''
    print command

def get_filetype(filepath):
    import imghdr
    fileType = imghdr.what(filepath)
    if fileType:
        fileType = "image"
    else:
        fileType = "notImage"
    return fileType

####################################################################
#
# main
#
####################################################################
args = argparse()
yamlFile = args.yamlfile
basepath = args.basepath
experimentVersion = args.experimentVersion
experimentType = args.experimentType
genomeOrganism = args.genomeOrganism
genomeVersion = args.genomeVersion
userName = args.username

# Read yaml
inStream = open(os.path.join(basepath, yamlFile), 'r')
yamlData = load(inStream, Loader=Loader)

# Get user & genome
author_modified =User.objects.get(username=userName)
refGenome = Genome.objects.get(organism__organismcode=genomeOrganism, version=genomeVersion)

# clean up/overwrite loaded data
if args.overwrite:
    if Experiment.objects.filter(name = yamlData['Global']['meta']['longtitle'], version=experimentVersion).exists():
        print "Version %s of the Experiment %s exists. I'm overwriting it in 10 seconds" %(experimentVersion,  yamlData['Global']['meta']['longtitle'])
        time.sleep(2)
        e =  Experiment.objects.get(name = yamlData['Global']['meta']['longtitle'], version=experimentVersion)
        e.delete()

print ("loading Experiments...")
# Experiment Model
newExpObj = Experiment()
newExpObj.version = experimentVersion
newExpObj.name = yamlData['Global']['meta']['longtitle']
newExpObj.type = experimentType
newExpObj.refgenome = refGenome
newExpObj.description = yamlData['Global']['meta']['longtitle']
newExpObj.author_modified = author_modified
newExpObj.save()

# get the saved object back.
expObj = Experiment.objects.get(name = yamlData['Global']['meta']['longtitle'], version=experimentVersion)

print ("create library code-name dictionary")
libraryNameCodeMap = dict()
for libname, libcode in yamlData['Global']['map'].items():
    libraryNameCodeMap[libname]=libcode
print(libraryNameCodeMap)

print ("loading Exptfiles...")
for category, filename in yamlData['Global']['meta']['exptfiles'].items():
    print "\t%s: %s" %(category, filename)
    newExptfileObj = Exptfile(experiment=expObj, category="detest")
    newExptfileObj.subcategory = category
    path = os.path.join(basepath, filename)
    newExptfileObj.filetype = get_filetype(path)
    newExptfileObj.file.save(filename, File(open(path)))

# Tagcount Model
print ("prepping Tagcounts...")
rawCountsFile = yamlData['Global']['meta']['countfiles']['rawcounts_file']
normCountsFile = yamlData['Global']['meta']['countfiles']['normalizedcounts_file']

rawCountsDic = hasify_counts(rawCountsFile, basepath)
normCountsDic = hasify_counts(normCountsFile, basepath)

print ("loading Tagcounts...")
for libname, countDic in rawCountsDic.items():
    libcode = libraryNameCodeMap[libname]
    print "\tlibrary code: %s; library name %s" %(libcode, libname)
    for featureID, rawCount in countDic.items():
        newTagcountObj = Tagcount(experiment=expObj, library=Library.objects.get(library_code=libcode), feature=featureID)
        newTagcountObj.rawcount = rawCountsDic[libcode][featureID]
        newTagcountObj.normalizedcount = normCountsDic[libcode][featureID]
        newTagcountObj.save()


print ("loading Exptsetup...")
# Exptsetup Model
for groupname, groupdic in yamlData['Global']['meta']['exptsetup'].items():
    print "\tgroupname: %s" %(groupname.upper())
    newExptsetup = Exptsetup(experiment=expObj)
    newExptsetup.groupname = groupname.upper()
    newExptsetup.author_modified = author_modified
    newExptsetup.save()
    # add lib, notes to it
    for key, values in groupdic.items():
        if key == 'libs':
            libcodes = values.split(",")
            newExptsetup.libraries = Library.objects.filter(library_code__in=libcodes)
        if key == 'notes':
            newExptsetup.notes = values
        newExptsetup.save()

print ("loading Comparisons...")
# Comparison, Compfiles Models
for contrastName, contrastDic in yamlData['Contrasts'].items():
    newComp = Comparison(experiment=expObj)
    print "\tcomparison name: %s "%contrastName
    newComp.compname = contrastName
    newComp.basegroup = Exptsetup.objects.get(groupname=contrastDic['basegroup'], experiment=expObj)
    newComp.querygroup = Exptsetup.objects.get(groupname=contrastDic['querygroup'], experiment=expObj)
    newComp.author_modified = author_modified
    newComp.save()

    compObj = Comparison.objects.get(experiment=expObj, compname=contrastName)
    # Compfiles Model
    print ("\tloading Compfiles...")
    for category, filename in yamlData['Contrasts'][contrastName]['compfiles'].items():
        print "\t\tloading %s "%filename
        newCompfileObj = Compfile(comparison=compObj, category="detest")
        newCompfileObj.subcategory = category
        path = os.path.join(basepath, filename)
        newCompfileObj.filetype = get_filetype(path)
        newCompfileObj.file.save(filename, File(open(path)))
    print ("\tloading Resultfiles...")
    deresultFile =  yamlData['Contrasts'][contrastName]['resultfiles']['DEresult']
    print "\t\tloading %s "%deresultFile
    deResult = open(os.path.join(basepath, deresultFile), 'r')
    deResult.readline()#remove headerline
    for line in deResult:
        #print(line)
        [id, feature, log2foldchange, logcpm, lr, pvalue, fdr, product] = line.split("\t")
        newDiffexpnObj = Diffexpn(experiment=expObj, compname=compObj, feature=feature, log2foldchange=log2foldchange, lr=lr, fdr=fdr, pvalue=pvalue)
        newDiffexpnObj.save()





