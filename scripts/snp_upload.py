#!/bin/bash


#  Purpose: Fill SNP postgres database from vcf output.
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

stat_cv = dict()
effect_cv = dict()
filter_cv = dict()

cur.execute('SELECT cvterm, stats_cvterm_id FROM "snpdb_statistics_cv"')
stats = cur.fetchall()
for each in stats:
	stat_cv[each[0]] = each[1]


cur.execute('SELECT effect_name, effect_id FROM "snpdb_effect_cv"')
eff = cur.fetchall()
for each in eff:
	effect_cv[each[0]] = each[1]


cur.execute('SELECT filter_type, filter_cv_id FROM "snpdb_filter_cv"')
filt = cur.fetchall()
for each in filt:
	filter_cv[each[0]] = each[1]


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


# Inserts statistic cvs from the INFO metadata into statistics cv when they are not already present.
# This information will be pulled to fill in the statistics table.
def insert_statistics_cv(infos, formats):
	for cv_name, value in infos.iteritems():
		cv_definition = value[3]
		if cv_name != "EFF":
			try:
				if cv_name in stat_cv:
					pass
				else:
					cur.execute('INSERT INTO "snpdb_statistics_cv" (cvterm, cv_notes) VALUES (%s, %s)',
					            (cv_name, cv_definition))
					dbh.commit()
			except psycopg2.IntegrityError, e:
				print "Inserting statistics rollback error", e
				dbh.rollback()
	for cv_name, values in formats.iteritems():
		cv_definition = values[3]
		if cv_name != "EFF":
			try:
				if cv_name in stat_cv:
					pass
				else:
					cur.execute('INSERT INTO "snpdb_statistics_cv" (cvterm, cv_notes) VALUES (%s, %s)',
					            (cv_name, cv_definition))
					dbh.commit()
			except psycopg2.IntegrityError, e:
				print "Inserting statistics cv rollback error", e
				dbh.rollback()


# Inserts the possible snp types into snp_type if they do not already exist.
# This information will be pulled for the snp_result table.
# May create redundant entries as it is unable to check for previous entries.
def insert_snp_type(snp_id, indel, deletion, is_snp, monomorphic, transition, sv):
	try:
		cur.execute(
			'INSERT INTO "snpdb_snp_type" (snp_id, indel, deletion, is_snp, monomorphic, transition, sv) VALUES (%s, %s, %s, %s, %s, %s, %s)',
			(snp_id, indel, deletion, is_snp, monomorphic, transition, sv))
		dbh.commit()
	except psycopg2.IntegrityError, e:
		print "Snp type rollback error", e
		dbh.rollback()


# This table inserts each type of snp for the snp_result table. The snp_id is pulled from the snp_type table.
def insert_snp_results(snp_position, result_id, ref_base, alt_base, heterozygosity, quality, library_id, chromosome_id, vcf_id):
	alt_bases = str(alt_base).strip('[]')
	try:
		cur.execute(
			'INSERT INTO "snpdb_snp" (snp_position, result_id, ref_base, alt_base, heterozygosity, quality, library_id, chromosome_id, vcf_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING snp_id',
			(snp_position, result_id, ref_base, alt_bases, heterozygosity, quality, library_id, chromosome_id, vcf_id))
		snp_id = cur.fetchone()[0]
		dbh.commit()
		return snp_id
	except psycopg2.IntegrityError, e:
		print "Snp result rollback error", e
		dbh.rollback()


# Inserts types of snp effects into effect_cv if they are not already listed.
# Effects are collected from the INFO metadata where id=EFF.
# Effect id will be pulled to fill in the effect table.
def insert_effect_cv(effect_list):
	eff_cv = re.findall('[\||\(][\s+](\w*)', effect_list)
	for all_effect in eff_cv:
		try:
			if all_effect in effect_cv:
				pass
			else:
				cur.execute('INSERT INTO "snpdb_effect_cv" (effect_name) VALUES (%s)', (all_effect,))
				dbh.commit()
		except psycopg2.IntegrityError:
			print "Effect cv rollback error"
			dbh.rollback()


# Inserts the snp_effects for each snp. Each effect type is grouped using the group_id. Effect_id is specific to one vcf file.
# May need to be adjusted in the future.
def insert_effect(snp_id, effect_class, effect_strings, effect_group, effect_list):
	effect = re.findall('[\||\(][\s+](\w*)', effect_list)
	effect_position = 0
	for effect_string in effect_strings:
		if effect_string:
			try:
				cur.execute('SELECT effect_id FROM "snpdb_effect_cv" WHERE effect_name = %s', (effect[effect_position],))
				effect_id = cur.fetchone()[0]
				cur.execute('INSERT INTO "snpdb_effect" (snp_id, effect_id, effect_class, effect_string, effect_group) VALUES (%s, %s, %s, %s, %s)',
				            (snp_id, effect_id, effect_class, effect_string, effect_group,))
				dbh.commit()
			except psycopg2.IntegrityError:
				print "no effect insert"
				dbh.rollback()
			effect_position += 1
		else:
			effect_position += 1


# Checks to see if the database contains the chromosome. If it does, the database connection is closed.
# If the chromosome is not present, it is added into the database. This is done before adding any of the snp_results.
def insert_chromosome(chromosome_name, organismcode, genome_version, genome_id):
	for chrom in chromosome_name:
		chromosome_fullname = chrom[0]
		size = chrom[1]
		chromosome = chromosome_fullname.split('_')[0]
		try:
			cur.execute('SELECT chromosome_id FROM "snpdb_chromosome" WHERE chromosome_name = %s AND genome_version = %s AND genome_name_id=%s',
			            (chromosome, genome_version, organismcode))
			chromosome_id = cur.fetchone()
			if chromosome_id is not None:
				return chromosome_id[0]
			else:
				cur.execute('SELECT chromosome FROM "ngsdbview_feature" WHERE chromosome=%s AND genome_id=%s', (chromosome, genome_id))
				cro = cur.fetchone()
				if cro is not None:
					cur.execute('INSERT INTO "snpdb_chromosome" (chromosome_name, size, genome_name_id, genome_version) VALUES (%s, %s, %s, %s)',
					            (chromosome, size, organismcode, genome_version))
					print "inserted chromosome into snpdb_chromosome"
				else:
					print "The chromosome", chromosome, "was not found in the Feature Table. Please upload the genome (.gff file) to Feature before proceeding."
					dbh.rollback()
					sys.exit()
		except psycopg2.IntegrityError:
			print "No chromosome inserted"
			dbh.rollback()
	dbh.commit()


# Identifies the chromosome ID if in the database. If not, prompts the user to add the chromosome.
def get_chromosome_id(chromosome, genome_version):
	try:
		chromosome_name = chromosome.split('_')[0]
		cur.execute('SELECT chromosome_id FROM "snpdb_chromosome" WHERE chromosome_name = %s AND genome_version = %s',
		            (chromosome_name, genome_version))
		chromosome_id = cur.fetchone()
		if chromosome_id is not None:
			return chromosome_id[0]
		else:
			print "Please add the chromosome to the ngsdb database."
	except psycopg2.IntegrityError:
		print "No chromosome ID"
		dbh.rollback()
	dbh.commit()


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


# Called from insert results to handle the second option chosen by the user.
# Manually deletes any entries connected with the snp in a cascade of events. Can be time consuming.
def insert_result_option2(result_ids, library_id, genome_id, author_id, analysis_path, timepoint):
	notes = ''
	try:
		for result in result_ids:
			result_to_delete = result[0]
			cur.execute('SELECT snp_id FROM "snpdb_snp" WHERE result_id =%s', (result_to_delete,))
			snps = cur.fetchall()
			for ids in snps:
				identifiers = ids[0]
				cur.execute('DELETE FROM "snpdb_statistics" WHERE snp_id=%s', (identifiers,))
				cur.execute('DELETE FROM "snpdb_filter" WHERE snp_id=%s', (identifiers,))
				cur.execute('DELETE FROM "snpdb_effect" WHERE snp_id=%s', (identifiers,))
				cur.execute('DELETE FROM "snpdb_snp_type" WHERE snp_id=%s', (identifiers,))
			cur.execute('DELETE FROM "snpdb_snp" WHERE result_id = %s', (result_to_delete,))
			cur.execute('DELETE FROM "ngsdbview_result_libraries" WHERE result_id = %s AND library_id = %s', (result_to_delete, library_id,))
			dbh.commit()
		cur.execute('INSERT INTO "ngsdbview_result" (genome_id, author_id, analysisPath, notes, is_current, is_obsolete, time_data_loaded) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING result_id',
		            (genome_id, author_id, analysis_path, notes, True, False, timepoint))
		new_result_id = cur.fetchone()[0]
		cur.execute('INSERT INTO "ngsdbview_result_libraries" (result_id, library_id) VALUES (%s, %s) RETURNING result_id',
		            (new_result_id, library_id))
		second_result_id = cur.fetchone()[0]
		return second_result_id
	except psycopg2.IntegrityError as err:
		print err
		print "Insert Result 2 rollback error"
		dbh.rollback()


# Collects the result_id. User is presented with three options if a result and library are already present in database.
def get_result(library_id, genome_id, author_id, analysis_path):
	timepoint = datetime.datetime.now()
	try:
		cur.execute('SELECT result_id FROM "ngsdbview_result_libraries" WHERE library_id = %s', (library_id,))
		result_ids = cur.fetchall()
		if result_ids:
			user_opt = input("There is already a result_id attached to this library. Please choose one of the"
			                 " following options."
			                 "\n1. Quit"
			                 "\n2. Override the old snp_results with these results. This will delete the old results. "
			                 "\n3. Keep old results and add these results under a new result_id. "
			                 "The old results will be marked as obsolete in the database. ")
			if user_opt == 1:
				sys.exit("You have quit the program. SNP_Results were not uploaded into the database.")
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
				cur.execute('INSERT INTO "ngsdbview_result" (genome_id, author_id, analysisPath, notes, is_current, is_obsolete, time_data_loaded) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING result_id',
				            (genome_id, author_id, analysis_path, notes, True, False, timepoint))
				result_id = cur.fetchone()[0]
				dbh.commit()
				return result_id
		else:
			notes = 'notes'
			cur.execute('INSERT INTO "ngsdbview_result" (genome_id, author_id, is_current, is_obsolete, analysisPath, notes, time_data_loaded) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING "result_id"',
			            (genome_id, author_id, True, False, analysis_path, notes, timepoint))
			result_id = cur.fetchone()[0]
			cur.execute('INSERT INTO "ngsdbview_result_libraries" (result_id, library_id) VALUES (%s, %s)', (result_id, library_id))
			dbh.commit()
			return result_id
	except psycopg2.IntegrityError, e:
		print "Getting result id rollback error"
		print e.pgerror
		dbh.rollback()


# Determines if the snp is heterozygous. Built in pyvcf function.
def get_heterozygosity(samples):
	for call in samples:
		heterozygosity = call.is_het
		return heterozygosity


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


def insert_snp_statistics(snp_id, cv_name, cv_value):
	try:
		cvterm_id = stat_cv.get(cv_name)
		if cvterm_id is not None:
			cur.execute('INSERT INTO "snpdb_statistics" (snp_id, stats_cvterm_id, cv_value) VALUES (%s, %s, %s)',
			            (snp_id, cv_name, cv_value))
		else:
			pass
	except psycopg2.IntegrityError:
		print "Inserting snp statistics rollback error"
		dbh.rollback()
	dbh.commit()


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


# Inserts any filters that a snp failed on.
def insert_filter_cv(filter_type):
	try:
		if filter_type:
			filter_string = filter_type[0]
			# filter_cv_id = filter_cv[filter_string]
			filter_cv_id = filter_cv.get(filter_string)
			if filter_cv_id is None:
				cur.execute('INSERT INTO "snpdb_filter_cv" (filter_type) VALUES (%s) RETURNING "filter_cv_id"', (filter_string,))
				filter_cv_id = cur.fetchone()
			dbh.commit()
			return filter_cv_id
	except psycopg2.IntegrityError:
		print "Filter cv insert rollback error"
		dbh.rollback()


# Inserts filters into the Filter table. Always inserts the filter as Failed.
def insert_filter(snp_id, filter_cv_id):
	filter_result = False
	try:
		cur.execute('INSERT INTO "snpdb_filter" (snp_id, filter_result, filter_cv_id) VALUES (%s, %s, %s)',
		            (snp_id, filter_result, filter_cv_id,))
		dbh.commit()
	except psycopg2.IntegrityError, e:
		print "inserting filter rollback error", e
		dbh.rollback()


def insert_vcf_file(library_id, result_id, vcf_file, vcf_path):
	vcf_md5sum = hashlib.md5()
	f= open(vcf_path)
	for line in f:
		vcf_md5sum.update(line)
	f.close()
	project_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
	vcf_name =  os.path.join('VCF_Files', os.path.basename(vcf_path))
	vcf_dir_path = os.path.join(project_dir, vcf_name)
	modified_time = time.ctime(os.path.getmtime(vcf_path))
	upload_time = str(datetime.datetime.now())
	cur.execute('INSERT INTO "snpdb_vcf_files" (vcf_path, library_id, result_id, vcf_md5sum, date_modified, date_uploaded) VALUES (%s, %s, %s, %s, %s, %s) RETURNING "vcf_id"',
	            (vcf_name, library_id, result_id, vcf_md5sum.hexdigest(), modified_time, upload_time))
	vcf_id = cur.fetchone()
	print vcf_id
	cmd = """cp %s %s"""
	subprocess.Popen(cmd % (vcf_path, vcf_dir_path), shell=True, stdout=subprocess.PIPE)
	return vcf_id


def insert_analysis(software_id, analysis_type, result_id, GATK_software_id, GATK_analysis_type):
	time_data_loaded = str(datetime.datetime.now())
	# Inserts the annotation of the vcf file using SNP Eff. Second step in the SNP analysis
	cur.execute('INSERT INTO "ngsdbview_analysis" (analysistype_id, software_id, result_id, ordinal, time_data_loaded, notes) VALUES (%s, %s, %s, %s, %s, %s) '
	            'RETURNING "analysis_id"',
	            (analysis_type, software_id, result_id, 2, time_data_loaded, ''))
	analysis_id = cur.fetchone()
	# inserts the creation of vcf files. First step for SNP analysis
	cur.execute('INSERT INTO "ngsdbview_analysis" (analysistype_id, software_id, result_id, ordinal, time_data_loaded, notes) VALUES (%s, %s, %s, %s, %s, %s)',
	            (GATK_analysis_type, GATK_software_id, result_id, 1, time_data_loaded, ''))
	return analysis_id


def insert_analysis_prop(analysis_id, analysis_command):
	cur.execute('INSERT INTO "ngsdbview_analysisprop" (analysis_id, cvterm_id, value) VALUES (%s, %s, %s)',
		(analysis_id, 2, analysis_command))


#todo Add command to upload analysis information
def main():
	snp_iterator = 0
	# Reads the file in from the command line. First file is the script, second is the vcf file,
	# and an option second is the summary file.
	num_of_files = len(sys.argv[1:])
	vcf_path = sys.argv[1]

	# If only a vcf file. Will be adjusted to automatically no through the command line input.
	if num_of_files == 1:
		print "Please note that without a summary file, the snp_summary & summary_level_cv table will not be updated. " \
		      "This can be done manually at a later date"
		# collect and import vcf file.
		vcf_reader = vcf.Reader(open(vcf_path, 'r'))
		vcf_file = File(vcf_reader)
		record = vcf_reader.next()

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

		# SQL Inserts and Selects
		#----------------------------------------------------------------------
		# Collects the organism_id from librarycode
		organism_id = get_organism_id(genome_id, genome_version)
		organismcode = get_organismcode(organism_id)

		# Collects the author_id from the Library table.
		author_id = get_author_id(librarycode)

		# Collects the library_id from the library table.
		library_id = get_library_id(librarycode)

		# Collects the result_id from results if already present, otherwise results are inserted into the table by
		# calling insert_result().
		result_id = get_result(library_id, genome_id, author_id, analysis_path)

		#Inserts vcf file int vcf_files table.
		vcf_id = insert_vcf_file(library_id, result_id, vcf_file, vcf_path)

		# Identifies the chromosome and chromosomal version
		chromosome_name = vcf_reader.contigs.values()
		insert_chromosome(chromosome_name, organismcode, genome_version, genome_id)

		# Inserts Statistic CVs into the Statistics_CV.
		info = vcf_reader.infos
		formats = vcf_reader.formats
		insert_statistics_cv(info, formats)


		# Collects analysis information for the annotation of SNPs
		analysis_command = vcf_reader.metadata['SnpEffCmd'][0].strip('"')
		software_algorithm = analysis_command.split()[0]
		software_version = vcf_reader.metadata['SnpEffVersion'][0].strip('"').split()[0]
		print "snp command: ", analysis_command

		try:
			cur.execute('SELECT software_id FROM "ngsdbview_software" WHERE name=%s AND version=%s and algorithm=%s',
			            ('SnpEff', software_version, software_algorithm))
			software_id = cur.fetchone()
		except psycopg2.IntegrityError:
			print "Getting software id rollback error"
			dbh.rollback()

		try:
			cur.execute('SELECT analysistype_id FROM "ngsdbview_analysistype" WHERE type=%s', ('SNP',))
			analysistype_id = cur.fetchone()
		except psycopg2.IntegrityError:
			print "Getting analysis type id rollback error"
			dbh.rollback()

		try:
			cur.execute('SELECT software_id FROM "ngsdbview_software" WHERE name=%s', ('GATK',))
			GATK_software_id = cur.fetchone()
		except psycopg2.IntegrityError:
			print "Getting software id rollback error"
			dbh.rollback()

		try:
			cur.execute('SELECT analysistype_id FROM "ngsdbview_analysistype" WHERE type=%s', ('GATK',))
			GATK_analysistype_id = cur.fetchone()
		except psycopg2.IntegrityError:
			print "Getting analysis type id rollback error"
			dbh.rollback()

		analysis_id = insert_analysis(software_id, analysistype_id, result_id, GATK_software_id, GATK_analysistype_id)

		insert_analysis_prop(analysis_id, analysis_command)


		# Inserts Effect types into effect_cv
		try:
			effect_list = vcf_reader.infos['EFF'].desc
			insert_effect_cv(effect_list)
		except KeyError:
			print "There are no effects present."
		#Attributes that are unique for each SNP.
		for snps in vcf_reader:
			chromosome = snps.CHROM
			snp_iterator += 1
			print snp_iterator
			ref_base = snps.REF
			alt_base = snps.ALT
			quality = snps.QUAL
			filter_type = snps.FILTER
			position = snps.POS
			is_snp = snps.is_snp
			indel = snps.is_indel
			deletion = snps.is_deletion
			monomorphic = snps.is_monomorphic
			sv = snps.is_sv       # structural variant
			transition = snps.is_transition
			statistics = snps.INFO


			# Returns the heterozygosity of each snp.
			samples = snps.samples
			heterozygosity = get_heterozygosity(samples)

			# Returns the chromosome_id for each snp result.
			chromosome_id = get_chromosome_id(chromosome, genome_version)

			# Inserts each snp_results into the snp table
			snp_id = insert_snp_results(position, result_id, ref_base, alt_base, heterozygosity, quality, library_id, chromosome_id, vcf_id)

			# Inserts the SNP types.
			insert_snp_type(snp_id, indel, deletion, is_snp, monomorphic, transition, sv)

			# Inserts effects on each SNP into Effect.
			try:
				effects = snps.INFO['EFF']
				group_id = 0
				for effs in effects:
					group_id += 1
					effect_class = effs.split('(')[0]
					effect_string = re.split('\((\S*\|\S*)\)', effs)[1]
					effects_string = effect_string.split('|')
					insert_effect(snp_id, effect_class, effects_string, group_id, effect_list)
			except KeyError:
				print "There are no effects."

			# Inserts the snp's statistics into Statistics
			for cv_name in statistics:
				cv_value = statistics[cv_name]
				if isinstance(cv_value, list):
					for values in cv_value:
						insert_snp_statistics(snp_id, cv_name, values)
				else:
					insert_snp_statistics(snp_id, cv_name, cv_value)

			# Checks to see if the snp failed on a filter. If so then inserts into filter table.
			if filter_type:
				filter_cv_id = insert_filter_cv(filter_type)
				insert_filter(snp_id, filter_cv_id)

	# NEED A STANDARD SUMMARY FILE
	elif num_of_files == 2:
		# collect and import vcf file.
		pass

	else:
		print "A vcf file is required for this program. Please try again."


main()