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
from samples.models import Library, Sample, Source, User

from ngsdbview.models import Library as ngsdbviewlibrary, Protocol as ngsdbviewprotocol
from ngsdbview.models import Author, Collaborator, Genotype, Growthphase, Lifestage, Organism, Phenotype, User
import yaml
from xlrd import open_workbook, cellname, cellnameabs, colname, xldate_as_tuple
from datetime import date



####################################################################
#
# Functions
#
####################################################################
def argparse():
    import argparse
    parser = argparse.ArgumentParser(description='Uploads RiboProfiling count data into Ngsdb03+.')
    parser.add_argument('--inputfile', required=False, help='the input spread sheet file with sample data')
    parser.add_argument('--sheetname', required=False, help='name of the sheet containing the data')
    parser.add_argument('--migratefromLibrary', required=False, help='When set (and supplied with comma separated libcodes, migrates those libraries from library to sample')
    parser.add_argument('--version', '-v',  action='version', version='%(prog)s 1.0')
    args = parser.parse_args()
    return args


def get_libs_with_samplename():
    libraries = Library.objects.all().exclude(sample_name="")
    return libraries



def migrate_library2sample_ingoringSpreadsheet(lib):
        # check if its been migrated already
        if Sample.objects.filter(sampleid=lib.sample_name).exists():
            print "Library ", lib.library_code, "has been migrated already, skipping."
        else:
            #create an new samples.sample object
            newsampleobj = Sample(organism=lib.organism, lifestage=lib.lifestage, growthphase=lib.growthphase, phenotype=lib.phenotype, genotype=lib.genotype, source=lib.source, sourcename=Source.objects.get(pk=1), sample_concentration=0, sample_volume=0, sample_quantity=0, author_modified=User.objects.get(username="gramasamy"))

            newsampleobj.sampleid = 's' + lib.library_code
            if lib.sample_name:
                newsampleobj.sampleid = lib.sample_name
            newsampleobj.date_created = lib.date_created
            if lib.sample_notes != 'NA':
                newsampleobj.sample_notes = lib.sample_notes
            if lib.experiment_notes  != 'NA':
                newsampleobj.sample_notes = newsampleobj.sample_notes + ' ' + lib.experiment_notes
            newsampleobj.collected_on = lib.collected_on
            newsampleobj.collected_at = lib.collected_at
            newsampleobj.collected_by = lib.collected_by
            newsampleobj.treatment = lib.treatment
            newsampleobj.collaborator = lib.collaborator
            newsampleobj.sampletype = 'RNA'

            #now save it
            newsampleobj.save()

            # save back sampleid into library table
            lib.sampleid = newsampleobj
            lib.save()




def hasify_sample_spreadsheet(file, sheetname, hashby, load_orphan_samples):
    data = {}
    book = open_workbook(file)
    sheet = book.sheet_by_name(sheetname)
    print "sheet ", sheet.name, "has ", sheet.nrows, "rows."
    for row in range(sheet.nrows):
        print "row:", row
        rowdic = {}
        sampleid = sheet.cell(row, 0).value
        librarycode = sheet.cell(row, 1).value

        rowdic['sampleid']=sheet.cell(row, 0).value
        rowdic['librarycode']=sheet.cell(row, 1).value
        rowdic['oncap']=sheet.cell(row, 2).value
        rowdic['ontube']=sheet.cell(row, 3).value
        rowdic['pi']=sheet.cell(row, 4).value
        rowdic['sender']=sheet.cell(row, 5).value
        rowdic['senderemailid']=sheet.cell(row, 6).value
        rowdic['genus']=sheet.cell(row, 7).value
        rowdic['species']=sheet.cell(row, 8).value
        rowdic['strain']=sheet.cell(row, 9).value
        rowdic['genotype']=sheet.cell(row, 10).value
        rowdic['stage']=sheet.cell(row, 11).value
        rowdic['isolationmethod']=sheet.cell(row, 12).value
        rowdic['replicate']=sheet.cell(row, 13).value
        rowdic['strangenumber']=sheet.cell(row, 14).value
        rowdic['dilution']=sheet.cell(row, 15).value
        rowdic['numberontube']=sheet.cell(row, 16).value
        if row != 0:
            if sheet.cell(row, 17).value != '':
                rowdic['dateisolated']= date(*xldate_as_tuple(sheet.cell(row, 17).value, book.datemode)[:3])
            else:
                rowdic['dateisolated']=''
            if sheet.cell(row, 18).value != '':
                rowdic['daterecieved']= date(*xldate_as_tuple(sheet.cell(row, 18).value, book.datemode)[:3])
            else:
                rowdic['daterecieved']= '';
        else:
            rowdic['dateisolated']= sheet.cell(row, 17).value
            rowdic['daterecieved']= sheet.cell(row, 18).value

        rowdic['concentration']=0
        if sheet.cell(row, 19).value:
            rowdic['concentration']=sheet.cell(row, 19).value

        rowdic['volume']= 0
        if sheet.cell(row, 20).value:
            rowdic['volume']=sheet.cell(row, 20).value
        rowdic['quantity'] = 0
        if sheet.cell(row, 21).value:
            rowdic['quantity']=sheet.cell(row, 21).value
        rowdic['notesfromsender']=sheet.cell(row, 22).value
        rowdic['bioanalyzer']=sheet.cell(row, 23).value
        rowdic['freezerlocation']=sheet.cell(row, 24).value
        if row == 0:
            print rowdic
        else:
            if hashby == "sampleid":
                if librarycode != '':
                    data[sampleid]=rowdic
                else:
                    print "Sample with sampleid ", sampleid, "does not have a library code associated with it:"
                    if load_orphan_samples == "YES":
                        print "load_orphan_libraries is set to YES, so loading it....."
                        load_orphan_sample(rowdic)
                        print "loading ", sampleid, " done."
            elif hashby == "librarycode":
                data[librarycode]=rowdic

    print data

    return data


def load_orphan_sample(rowdic):
    print rowdic

    sampleid = rowdic['sampleid']

    newsampleobj = Sample()
    if Sample.objects.filter(sampleid=sampleid).exists():
        newsampleobj = Sample.objects.get(sampleid=sampleid)


    newsampleobj.sampleid = sampleid
    # Things not in spread sheet but essential
    newsampleobj.sampletype = "RNA"
    newsampleobj.growthphase = Growthphase.objects.get(growthphase="log")
    newsampleobj.phenotype = Phenotype.objects.get(phenotype="wildtype")
    newsampleobj.author_modified = User.objects.get(username="gramasamy")
    newsampleobj.sourcename = Source.objects.get(pk=1)
    # Things From spread sheet

    #
    parentsampleid = "None"
    if sampleid[-1].isdigit():
        parentsampleid = "None"
    else:
        parentsampleid = rowdic['sampleid'][:-1]
    print parentsampleid
    newsampleobj.parent_sampleid = parentsampleid;

    #
    label_ontube = rowdic['oncap']
    if rowdic['ontube']:
        label_ontube =  rowdic['oncap'] + ' / ' + rowdic['ontube']
    newsampleobj.label_ontube = label_ontube

    #
    newsampleobj.genotype = Genotype.objects.get(genotype=rowdic['genotype'])
    newsampleobj.lifestage = Lifestage.objects.get(lifestage=rowdic['stage'])
    print rowdic['genus']
    print rowdic['species']
    print rowdic['strain']
    print rowdic['dateisolated']
    newsampleobj.organism = Organism.objects.get(genus=rowdic['genus'], species=rowdic['species'], strain=rowdic['strain'])
    if rowdic['dateisolated']:
        newsampleobj.collected_on = rowdic['dateisolated']
    newsampleobj.collected_by = rowdic['sender']
    newsampleobj.collected_by_emailid = rowdic['senderemailid']
    newsampleobj.isolation_method = rowdic['isolationmethod']
    newsampleobj.sample_dilution = rowdic['dilution']
    if rowdic['daterecieved']:
        newsampleobj.date_received  = rowdic['daterecieved']
    newsampleobj.sample_concentration = rowdic['concentration']
    newsampleobj.sample_volume = rowdic['volume']
    newsampleobj.sample_quantity = rowdic['quantity']
    newsampleobj.biological_replicate_of = rowdic['replicate']

    newsampleobj.freezer_location = rowdic['freezerlocation']
    #
    newsampleobj.sample_notes = rowdic['notesfromsender']
    print rowdic['pi']
    newsampleobj.collaborator = Collaborator.objects.get(lastname=rowdic['pi'])

    print newsampleobj
    newsampleobj.save()



####################################################################
#
# main
#
####################################################################
args = argparse()
inputfile = args.inputfile
sheetname = args.sheetname
migratefromLibrary = args.migratefromLibrary

if migratefromLibrary:
    libcodes = migratefromLibrary.split(',')
    for libcode in libcodes:
        print ("migrating :"+libcode)
        lib = Library.objects.get(library_code=libcode)
        migrate_library2sample_ingoringSpreadsheet(lib)



elif inputfile:
    # hasify the spread sheet
    # Possibly load the rows into samples database when there is no library id is found.
    hashby = "sampleid"
    load_orphan_samples = "YES"
    sheetdata = hasify_sample_spreadsheet(inputfile, sheetname, hashby, load_orphan_samples)

    samples_notloaded = {}
    samples_loaded = {}
    libraries_appended = {}
    # load sample data for rows read from spreadsheet
    #
    for sampleid in sheetdata:
        print "Sample id:",sampleid
        rowdic = sheetdata[sampleid]
        print "\t", rowdic
        librarycode = rowdic['librarycode']

        #some samples have two or more libraries generated outof them
        librarycodes = librarycode.split("/")
        librarycode = librarycodes[0]
        print "Library codes:", librarycodes
        print "library code :", librarycode
        libobj = ""
        if Library.objects.filter(library_code=librarycode).exists():
            libobj = Library.objects.get(library_code=librarycode)


            #check if the sample is loaded into Samples.sample already.
            #
            sampleobj = Sample()
            if Sample.objects.filter(sampleid=sampleid).exists():
                sampleobj = Sample.objects.get(sampleid=sampleid)

            sampleobj.sampleid = sampleid
            sampleobj.sampletype = 'RNA'

            #
            label_ontube = rowdic['oncap']
            if rowdic['ontube']:
                label_ontube =  rowdic['oncap'] + ' / ' + rowdic['ontube']
            sampleobj.label_ontube = label_ontube

            # from library object
            sampleobj.organism = libobj.organism
            sampleobj.lifestage = libobj.lifestage
            sampleobj.growthphase = libobj.growthphase
            sampleobj.phenotype = libobj.phenotype
            sampleobj.genotype = libobj.genotype
            sampleobj.collaborator = libobj.collaborator
            sampleobj.source = libobj.source
            sampleobj.sourcename = Source.objects.get(pk=1)
            sampleobj.treatment = libobj.treatment
            sampleobj.collected_at  = libobj.collected_at

            # from spread sheet
            if rowdic['dateisolated']:
                sampleobj.collected_on = rowdic['dateisolated']
            sampleobj.collected_by = rowdic['sender']
            sampleobj.collected_by_emailid = rowdic['senderemailid']
            sampleobj.isolation_method = rowdic['isolationmethod']
            if rowdic['daterecieved']:
                sampleobj.date_received = rowdic['daterecieved']
            sampleobj.sample_concentration = rowdic['concentration']
            sampleobj.sample_volume = rowdic['volume']
            sampleobj.sample_quantity = rowdic['quantity']
            sampleobj.sample_dilution = rowdic['dilution']
            sampleobj.biological_replicate_of = rowdic['replicate']
            sampleobj.freezer_location = rowdic['freezerlocation']
            sampleobj.sample_notes = libobj.sample_notes + "\n" + rowdic['notesfromsender']
            #
            parentsampleid = "None"
            if sampleid[-1].isdigit():
                parentsampleid = "None"
            else:
                parentsampleid = rowdic['sampleid'][:-1]
            print parentsampleid
            sampleobj.parent_sampleid = parentsampleid

            sampleobj.author_modified = User.objects.get(username="gramasamy")

            print sampleobj
            sampleobj.save()
            samples_loaded[sampleid]=sampleobj.id

            for librarycode in librarycodes:
                libobj = Library.objects.get(library_code=librarycode)
                libobj.sampleid = sampleobj
                libobj.save()
                libraries_appended[librarycode]=libobj.id
        else:
            samples_notloaded[sampleid]= librarycode + " does not exist in Library table"


    print "------------------------------------------------------------"
    print "Samples not loaded:"
    print samples_notloaded
    print "Samples  loaded:"
    print samples_loaded
    print "Libraries appended:"
    print libraries_appended

#libraries = Library.objects.all().exclude(sample_name="")
#for lib in libraries:
#    print ("migrating "+lib.library_code)
#    migrate_library2sample(lib)

