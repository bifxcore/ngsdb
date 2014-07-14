import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from django.core.management import setup_environ
os.environ['DJANGO_SETTINGS_MODULE'] = 'ngsdb03.settings.gowthamanlaptop'
from ngsdb03 import settings
setup_environ(settings)

from os.path import basename

from samples.models import Library

file = "/Users/gramasamy/djcode/ngsdb03/samples/scripts/fastqFiles.list.194.ALL.tab.goodones"
with open(file) as f:
    for line in f:
        cols = line.split("\t")
        librarycode = cols[0]
        fastq_size = cols[1]
        fastq_md5sum = cols[2]
        fastq_filename = cols[3]
        fastq_linecount = cols[4]
        fastq_readcount = int(fastq_linecount) / 4

        if Library.objects.filter(library_code=librarycode).exists():

            libobj = Library.objects.get(library_code=librarycode)
            print  libobj.fastqfile_name, ":"

            libobj.fastqfile_name=fastq_filename
            libobj.fastqfile_md5sum=fastq_md5sum
            libobj.fastqfile_readcount = fastq_readcount
            libobj.fastqfile_size_inbytes = fastq_size
            libobj.fastqfile_name
            libobj.save()
            print  libobj.fastqfile_name, "-"


        print librarycode


