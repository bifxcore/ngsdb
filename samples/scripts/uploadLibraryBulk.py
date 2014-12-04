#!/Users/gramasamy/virtualenv/ngsdb03/bin/python
# to execute this script from anywhere
import sys, os
sys.path.append('/Users/gramasamy/djcode/ngsdb03/')

from samples.models import *
from ngsdbview.models import *
from django.core.files import File
import os

####################################################################
#
# Functions
#
####################################################################
def argparse():
    import argparse
    parser = argparse.ArgumentParser(description='Uploads bulk data into Library and related tables.')
    parser.add_argument('--infile', required=True, help='the file that has tab delimited input for library table')
    parser.add_argument('--basepath',  required=True, help='Base path for the directory which contains all the files, including yaml.\n')
    parser.add_argument('--example', required=False, help="prints example input data and/ command")
    parser.add_argument('--version', '-v',  action='version', version='%(prog)s 1.0')
    args = parser.parse_args()
    return args

def example():
    example_input = '''
PA003	sPA003	PA	Alcolea	JVLINJ001	fragRNA	polyA_purified_mRNA	Genewiz_RNAseq_00	2014-07-30	2014-08-15	2014-09-26	H0V3EADXX	1,2	GATCAG	17464144	2855233730	36a8cec23d99cb3e2a0c46e92cbe8fc6	PA003.H0V3EADXX.lane1n2.indexGATCAG.R1.fastq,PA003.H0V3EADXX.lane1n2.indexGATCAG.R2.fastq
PA004	sPA004	PA	Alcolea	JVLINJ001	fragRNA	polyA_purified_mRNA	Genewiz_RNAseq_00	2014-07-30	2014-08-15	2014-09-26	H0V3EADXX	1,2	TAGCTT	17684019	2891187598	2818c9d35290410fddf8b38c759b0bf8	PA004.H0V3EADXX.lane1n2.indexTAGCTT.R1.fastq,PA004.H0V3EADXX.lane1n2.indexTAGCTT.R2.fastq
PA005	sPA005	PA	Alcolea	JVLINJ001	fragRNA	polyA_purified_mRNA	Genewiz_RNAseq_00	2014-07-30	2014-08-15	2014-09-26	H0V3EADXX	1,2	GGCTAC	17014268	2781679701	213475f6bd3ae222b4bfe46ac2c28075	PA005.H0V3EADXX.lane1n2.indexGGCTAC.R1.fastq,PA005.H0V3EADXX.lane1n2.indexGGCTAC.R2.fastq
PA006	sPA006	PA	Alcolea	JVLINJ001	fragRNA	polyA_purified_mRNA	Genewiz_RNAseq_00	2014-07-30	2014-08-15	2014-09-26	H0V3EADXX	1,2	GTCCGC	19839526	3243584994	1ab14b80b219313504eb89b5b8b1cda3	PA006.H0V3EADXX.lane1n2.indexGTCCGC.R1.fastq,PA006.H0V3EADXX.lane1n2.indexGTCCGC.R2.fastq
PA007	sPA007	PA	Alcolea	JVLINJ001	fragRNA	polyA_purified_mRNA	Genewiz_RNAseq_00	2014-07-30	2014-08-15	2014-09-26	H0V3EADXX	1,2	GTGAAA	16507448	2698823986	f0e442d40f6706eaa4542eae6e060115	PA007.H0V3EADXX.lane1n2.indexGTGAAA.R1.fastq,PA007.H0V3EADXX.lane1n2.indexGTGAAA.R2.fastq
PA008	sPA008	PA	Alcolea	JVLINJ001	fragRNA	polyA_purified_mRNA	Genewiz_RNAseq_00	2014-07-30	2014-08-15	2014-09-26	H0V3EADXX	1,2	ATGTCA	18696408	3056703819	f47637791c92893fd29570796020b450	PA008.H0V3EADXX.lane1n2.indexATGTCA.R1.fastq,PA008.H0V3EADXX.lane1n2.indexATGTCA.R2.fastq
PA009	sPA009	PA	Alcolea	JVLINJ001	fragRNA	polyA_purified_mRNA	Genewiz_RNAseq_00	2014-07-30	2014-08-15	2014-09-26	H0V3EADXX	1,2	CCGTCC	18392056	3006955571	ecfea8ec0ee19a5cd169036e98fc5293	PA009.H0V3EADXX.lane1n2.indexCCGTCC.R1.fastq,PA009.H0V3EADXX.lane1n2.indexCCGTCC.R2.fastq
PA010	sPA010	PA	Alcolea	JVLINJ001	fragRNA	polyA_purified_mRNA	Genewiz_RNAseq_00	2014-07-30	2014-08-15	2014-09-26	H0V3EADXX	1,2	CTTGTA	16439077	2687652514	d1b20237d2f4ba5436f84957e314e871	PA010.H0V3EADXX.lane1n2.indexCTTGTA.R1.fastq,PA010.H0V3EADXX.lane1n2.indexCTTGTA.R2.fastq
NC003	sNC003	JM	Carter	NCLDO0002	fragRNA	polyA_purified_mRNA	Genewiz_RNAseq_00	2014-09-10	2014-09-12	2014-09-29	H0V98ADXX	2	TAGCTT	31333675	5122726870	2a2e53c60f173cbea6714cb35504622c	NC003.HX.H0V98ADXX.lane2.indexTAGCTT.R1.fastq,NC003.HX.H0V98ADXX.lane2.indexTAGCTT.R2.fastq
NC004	sNC004	JM	Carter	NCLDO0002	fragRNA	polyA_purified_mRNA	Genewiz_RNAseq_00	2014-09-10	2014-09-12	2014-09-29	H0V98ADXX	2	GGCTAC	27697327	4528200315	4ce514a9a7605b0be6a4c9c5344a99b3	NC004.HYPA.H0V98ADXX.lane2.indexGGCTAC.R1.fastq,NC004.HYPA.H0V98ADXX.lane2.indexGGCTAC.R2.fastq
NC005	sNC005	JM	Carter	NCLDO0002	fragRNA	polyA_purified_mRNA	Genewiz_RNAseq_00	2014-09-10	2014-09-12	2014-09-29	H0V98ADXX	2	CTTGTA	29434397	4812216594	b520c20eb5fc707e8a8e724a09d0e0c2	NC005.HYPB.H0V98ADXX.lane2.indexCTTGTA.R1.fastq,NC005.HYPB.H0V98ADXX.lane2.indexCTTGTA.R2.fastq
NC006	sNC006	JM	Carter	NCLDO0002	fragRNA	polyA_purified_mRNA	Genewiz_RNAseq_00	2014-09-10	2014-09-12	2014-09-29	H0V98ADXX	2	AGTTCC	30221608	4940913672	42f557261097f57b100a454c7bc29be9	NC006.XANA.H0V98ADXX.lane2.indexAGTTCC.R1.fastq,NC006.XANA.H0V98ADXX.lane2.indexAGTTCC.R2.fastq
NC007	sNC007	JM	Carter	NCLDO0002	fragRNA	polyA_purified_mRNA	Genewiz_RNAseq_00	2014-09-10	2014-09-12	2014-09-29	H0V98ADXX	2	ATGTCA	33774495	5521768733	bd13f2590d326445835baf57958e481c	NC007.XANB.H0V98ADXX.lane2.indexATGTCA.R1.fastq,NC007.XANB.H0V98ADXX.lane2.indexATGTCA.R2.fastq
NC008	sNC008	JM	Carter	NCLDO0002	fragRNA	polyA_purified_mRNA	Genewiz_RNAseq_00	2014-09-10	2014-09-12	2014-09-29	H0V98ADXX	2	CCGTCC	29540222	4829498201	068f5db41899190ec35e9156db09b018	NC008.NO.H0V98ADXX.lane2.indexCCGTCC.R1.fastq,NC008.NO.H0V98ADXX.lane2.indexCCGTCC.R2.fastq
AS033	AT001	SC	Tomas	NCLDO0002	fragRNA	polyA_purified_mRNA	Genewiz_RNAseq_00	2014-05-26	2014-05-30	2014-06-26	FCC4U45	4	ACTTGA	28957420	3923200191	8d66d237954764e9b32e8b2a7dccd82b	AS033.FCC4U45.lane4.indexACTTGA.R1.ALL.thinned.fastq,AS033.FCC4U45.lane4.indexACTTGA.R2.ALL.thinned.fastq
AS034	AT002	SC	Tomas	NCLDO0002	fragRNA	polyA_purified_mRNA	Genewiz_RNAseq_00	2014-05-26	2014-05-30	2014-06-26	FCC4U45	4	GATCAG	24311141	3293713843	33e6c4dcae4e50db10416cf1550420db	AS034.FCC4U45.lane4.indexGATCAG.R1.ALL.thinned.fastq,AS034.FCC4U45.lane4.indexGATCAG.R2.ALL.thinned.fastq
AS035	AT003	SC	Tomas	NCLDO0002	fragRNA	polyA_purified_mRNA	Genewiz_RNAseq_00	2014-05-26	2014-05-30	2014-06-26	FCC4U45	4	TAGCTT	25482016	3452342409	253ec4242e4524597483d641231804d6	AS035.FCC4U45.lane4.indexTAGCTT.R1.ALL.thinned.fastq,AS035.FCC4U45.lane4.indexTAGCTT.R2.ALL.thinned.fastq
AS036	AT004	SC	Tomas	NCLDO0002	fragRNA	polyA_purified_mRNA	Genewiz_RNAseq_00	2014-05-26	2014-05-30	2014-06-26	FCC4U45	4	GGCTAC	22703655	3075928023	0b94beb1de4f1a6661fb9a5e3d0df17f	AS036.FCC4U45.lane4.indexGGCTAC.R1.ALL.thinned.fastq,AS036.FCC4U45.lane4.indexGGCTAC.R2.ALL.thinned.fastq
AS037	AT005	SC	Tomas	NCLDO0002	fragRNA	polyA_purified_mRNA	Genewiz_RNAseq_00	2014-05-26	2014-05-30	2014-06-26	FCC4U45	4	CTTGTA	27430371	3716322053	6f5282764b2ce96f7e0fdceedb6331fc	AS037.FCC4U45.lane4.indexCTTGTA.R1.ALL.thinned.fastq,AS037.FCC4U45.lane4.indexCTTGTA.R2.ALL.thinned.fastq
    '''
    print example_input


args = argparse()
if args.example:
    example()
    exit()

file = open(os.path.join(args.basepath, args.infile), "r")
for line in file:
    print line
    [libcode, sampleid, author, collaborator, bioproject, librarytype, template, protocol, libcreation, libsubmission, seqdownloaded, flowcell, lane, index, readcount, libbytesize, md5sum, fastqfilenames] = line.split()
    if author != 'XX':
        newLibObj = Library(library_code=libcode, sampleid=Sample.objects.get(sampleid=sampleid), template_material = 'polyA purified mRNA')
        newLibObj.author = Author.objects.get(designation=author)
        newLibObj.bioproject = Bioproject.objects.get(bioproject_code=bioproject)
        newLibObj.librarytype = Librarytype.objects.get(type=librarytype)
        newLibObj.protocol = Protocol.objects.get(protocol_name=protocol)
        newLibObj.library_creation_date = libcreation
        newLibObj.submitted_for_sequencing_on = libsubmission
        newLibObj.sequence_downloaded_on = seqdownloaded
        newLibObj.flowcell_number = flowcell
        newLibObj.collaborator = Collaborator.objects.get(lastname=collaborator)
        newLibObj.lane_number = lane
        newLibObj.index_sequence = index
        newLibObj.fastqfile_readcount = readcount
        newLibObj.fastqfile_size_inbytes = libbytesize
        newLibObj.fastqfile_md5sum = md5sum
        newLibObj.fastqfile_name = fastqfilenames
        newLibObj.author_modified = User.objects.get(username='gramasamy')
        newLibObj.suggested_reference_genome = "Genome: LinJ ; Version: 8.0"
        newLibObj.save()
