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

dbh = psycopg2.connect(host='ngsdb', database='ngsdb03ab', user='ngsdb03', password='ngsdb03')
cur = dbh.cursor()


# Identifies the organism_id from the Library table.
def get_organism_id(genome_id, genome_version):
	try:
		cur.execute('SELECT organism_id FROM "ngsdbview_genome" WHERE genome_id = %s',
		            (genome_id,))
		organism = cur.fetchone()
		if organism is not None:
			return organism[0]
		else:
			print "Please add organism or library to the ngsdb database."
	except psycopg2.IntegrityError:
		print "Organism Id Rollback error"
		dbh.rollback()


# Identifies the organism code from the Organism table through the organism id.
def get_organismcode(organism_id):
	try:
		cur.execute('SELECT organismcode FROM "ngsdbview_organism" WHERE organism_id = %s',
		            (organism_id,))
		organismcode = cur.fetchone()
		if organismcode is not None:
			return organismcode[0]
		else:
			print "Please add organism to the database."
	except psycopg2.IntegrityError:
		print "Getting organismcode rollback error"
		dbh.rollback()


# Identifies the library id from the Library table through the library code
def get_library_id(librarycode):
	try:
		cur.execute('SELECT id FROM "samples_library" WHERE library_code = %s', [librarycode])
		library_id = cur.fetchone()
		if library_id is not None:
			return library_id[0]
		else:
			print "Please manually add the library to ngsdb."
	except psycopg2.IntegrityError, e:
		print "Error in Library id", e


def get_result(library_id, genome_id, author_id, analysis_path):
	timepoint = datetime.datetime.now()
	try:
		cur.execute('SELECT result_id FROM "ngsdbview_result_libraries" WHERE library_id = %s', (library_id,))
		result_ids = cur.fetchall()

		tup_result = ()
		for each in result_ids:
			tup_result = tup_result + (each[0],)
		cur.execute('SELECT result_id FROM "ngsdbview_result" WHERE result_id IN %s AND result_type_cv_id = 3', (tup_result,))
		cnv_results = cur.fetchall()


		if cnv_results:
			user_opt = input("There is already a CNV result_id attached to this library. Please choose one of the"
			                 " following options."
			                 "\n1. Quit"
			                 "\n2. Override the old cnv_results with these results. This will delete the old results. "
			                 "\n3. Keep old results and add these results under a new result_id. "
			                 "The old results will be marked as obsolete in the database. ")
			if user_opt == 1:
				sys.exit("You have quit the program. CNV_Results were not uploaded into the database.")
			elif user_opt == 2:
				result_id = insert_result_option2(result_ids, library_id, genome_id, author_id, analysis_path, timepoint)
				dbh.commit()
				return result_id
			elif user_opt == 3:
				notes = ''
				for results in result_ids:
					result = results[0]
					cur.execute('UPDATE "ngsdbview_result" SET is_current = %s, is_obsolete = %s WHERE result_id = %s', (False, True, result,))
					dbh.commit()
				cur.execute('INSERT INTO "ngsdbview_result" (genome_id, author_id, analysisPath, notes, is_current, is_obsolete, time_data_loaded, result_type_cv_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING result_id',
				            (genome_id, author_id, analysis_path, notes, True, False, timepoint, 3))
				result_id = cur.fetchone()[0]
				dbh.commit()
				return result_id
		else:
			notes = 'notes'
			cur.execute('INSERT INTO "ngsdbview_result" (genome_id, author_id, is_current, is_obsolete, analysisPath, notes, time_data_loaded, result_type_cv_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING "result_id"',
			            (genome_id, author_id, True, False, analysis_path, notes, timepoint, 3))
			result_id = cur.fetchone()[0]
			cur.execute('INSERT INTO "ngsdbview_result_libraries" (result_id, library_id) VALUES (%s, %s)', (result_id, library_id))
			dbh.commit()
			return result_id
	except psycopg2.IntegrityError, e:
		print "Getting result id rollback error"
		print e.pgerror
		dbh.rollback()


# Called from insert results to handle the second option chosen by the user.
# Manually deletes any entries connected with the snp in a cascade of events. Can be time consuming.
def insert_result_option2(result_ids, library_id, genome_id, author_id, analysis_path, timepoint):
	notes = ''
	try:
		for result in result_ids:
			result_to_delete = result[0]
			# cur.execute('SELECT cnv_id FROM "snpdb_cnv" WHERE result_id =%s', (result_to_delete,))
			# cnvs = cur.fetchall()
			cur.execute('DELETE FROM "snpdb_cnv" WHERE result_id = %s', (result_to_delete,))
			cur.execute('DELETE FROM "ngsdbview_result_libraries" WHERE result_id = %s AND library_id = %s', (result_to_delete, library_id,))
			dbh.commit()
		cur.execute('INSERT INTO "ngsdbview_result" (genome_id, author_id, analysisPath, notes, is_current, is_obsolete, time_data_loaded, result_type_cv_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING result_id',
		            (genome_id, author_id, analysis_path, notes, True, False, timepoint, 3))
		new_result_id = cur.fetchone()[0]
		cur.execute('INSERT INTO "ngsdbview_result_libraries" (result_id, library_id) VALUES (%s, %s) RETURNING result_id',
		            (new_result_id, library_id))
		second_result_id = cur.fetchone()[0]
		return second_result_id
	except psycopg2.IntegrityError as err:
		print err
		print "Insert Result 2 rollback error"
		dbh.rollback()
	dbh.commit()


def get_chromosome(chrom, genome_version, genome_name):
	try:
		chromosome_name = chrom.split('_')[0]
		cur.execute('SELECT chromosome_id FROM "snpdb_chromosome" WHERE chromosome_name = %s AND genome_version = %s AND genome_name_id = %s',
		            (chromosome_name, genome_version, genome_name))
		chromosome_id = cur.fetchone()
		if chromosome_id is not None:
			return chromosome_id[0]
		else:
			print "Please add the chromosome to the ngsdb database."
	except psycopg2.IntegrityError:
		print "No chromosome ID"
		dbh.rollback()
	dbh.commit()


# Connects to the database and finds author_id from the Library table.
def get_author_id(librarycode):
	try:
		cur.execute('SELECT author_id FROM "samples_library" WHERE library_code = %s', (librarycode,))
		author_id = cur.fetchone()
		return author_id[0]
	except psycopg2.DatabaseError, e:
		#If an error occurs during the SELECT, the database will roll back any possible changes to the database.
		print 'Error %s' % e
		sys.exit(1)


def insert_cnv(chromosome, start, stop, cnv_value, library_id, result_id, window_size, coverage):
	try:
		cur.execute('INSERT INTO "snpdb_cnv" (chromosome_id, start, stop, cnv_value, library_id, result_id, window_size, coverage) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
		            (chromosome, start, stop, cnv_value, library_id, result_id, window_size, coverage))
	except psycopg2.DatabaseError, e:
		#If an error occurs during the SELECT, the database will roll back any possible changes to the database.
		print 'Error %s' % e
		dbh.rollback()
		sys.exit(1)
	dbh.commit()

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
		try:
			cur.execute('SELECT genome_id, organism_id, version FROM "ngsdbview_genome"s',
			            (librarycode,))
			genome = cur.fetchall()
			for genomes in genome:
				try:
					cur.execute('SELECT organismcode FROM "ngsdbview_organism" WHERE organism_id=%s', (genomes[1],))
					organismcode = cur.fetchone()
					print "{0}\t{1}\t{2}".format(genomes[0], organismcode[0], genomes[2])
				except psycopg2.IntegrityError:
					print "Getting organismcode rollback error"
					dbh.rollback()
		except psycopg2.IntegrityError:
			print "Getting genome id rollback error"
			dbh.rollback()

		genome_id = raw_input("Please state the genome_id. ")
		genome_version = raw_input("Please state the genome version. ")
		analysis_path = raw_input("Please provide the full analysis path. ")

		organism_id = get_organism_id(genome_id, genome_version)
		organismcode = get_organismcode(organism_id)

		library_id = get_library_id(librarycode)

		# Collects the author_id from the Library table.
		author_id = get_author_id(librarycode)

		result_id = get_result(library_id, genome_id, author_id, analysis_path)



		#Reads each line of file.
		for line in f:
			cnv = line.split()
			chrom = cnv[0]
			try:
				start = int(cnv[1])
				stop = int(cnv[2])
				cnv_value = cnv[4]
				coverage = cnv[3]
				window_size = int(stop) - int(start) + 1

				chromosome = get_chromosome(chrom, genome_version, organismcode)
				insert_cnv(chromosome, start, stop, cnv_value, library_id, result_id, window_size, coverage)

			except ValueError:
				pass




	# NEED A STANDARD SUMMARY FILE
	elif num_of_files > 1:
		print "You have submitted too many files. Please try the command again with only one CNV tab file."
		pass
	else:
		print "A cnv tab file is required for this program. Please try again."


main()