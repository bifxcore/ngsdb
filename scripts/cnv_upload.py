#
#  Purpose: Fill CNV postgres database from tab output.
#			Run interactively as script prompts for user input
#			in case of repeated attempts to load the same file.
#
#-------------------------------------------------------------------------------------------
import psycopg2
import sys
import re
import vcf
import datetime
import hashlib
import os.path, time
from django.core.files import File
import subprocess

dbh = psycopg2.connect(host='ngsdb', database='ngsdb03aa', user='ngsdb03', password='ngsdb03')
cur = dbh.cursor()

def main():
	# Reads the file in from the command line. First file is the script, second is the vcf file,
	# and an option second is the summary file.
	num_of_files = len(sys.argv[1:])
	cnv_path = sys.argv[1]

	# If only a vcf file. Will be adjusted to automatically no through the command line input.
	if num_of_files == 1:
		# collect and import cnv file.
		f = open(cnv_path, 'r')

		# Collects input from the user.
		#--------------------------------------------------------------------

		# Identifies the librarycode, librarycode, genome_id, and genome version,
		librarycode = raw_input("Please state the librarycode. ")

		#Reads each line of file.
		for line in f:
			print line

	# NEED A STANDARD SUMMARY FILE
	elif num_of_files > 1:
		print "You have submitted too many files. Please try the command again with only one CNV tab file."
		pass
	else:
		print "A cnv tab file is required for this program. Please try again."


main()