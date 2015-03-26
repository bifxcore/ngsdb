__author__ = 'mcobb'
from snpdb.models import *
from samples.models import *
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext
from utils import build_orderby_urls
from collections import *
import subprocess
import datetime
import os
import vcf
import ast
from math import ceil


# Displays the search page to compare two groups of libraries for unique and similar snps.
def compare_libs(request):
	ref_genome = request.GET.get('ref_genome')
	if ref_genome:
		lib_list = Library.objects.values('library_code', 'result__genome__organism__organismcode').filter(result__genome__organism__organismcode=ref_genome).distinct().order_by('library_code')
	else:
		lib_list = Organism.objects.values('organismcode').distinct().order_by('organismcode')
	page = request.GET.get('page')
	paginator = Paginator(lib_list, 500)

	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)
	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)
	return render_to_response('snpdb/compare_libraries.html', {"results": results,
	                                                           "ref_genome": ref_genome,
	                                                           "paginator": paginator,
	                                                           "toolbar_max": toolbar_max,
	                                                           "toolbar_min": toolbar_min}, context_instance=RequestContext(request))


def add_snps_from_vcf(vcf_file, libraries, group_libs, snp_dict, wt, impact):
	vcf_reader = vcf.Reader(open(vcf_file, 'r'))

	for record in vcf_reader:
		snp = defaultdict(set)
		pos = record.POS
		chrom = record.CHROM
		qual = record.QUAL
		ref = record.REF
		alt = ','.join(str(i) for i in record.ALT)
		genes = set()
		effects = record.INFO["ANN"]
		sample = vcf_reader.samples[0]
		hetero = False

		lib_dict = {}
		for lib in libraries:
			if lib in group_libs:
				lib_dict[lib] = {'ref': set(), 'alt': set(), 'effect': set()}
			else:
				lib_dict[lib] = {'ref': set(["Ref"]), 'alt': set(["Ref"]), 'effect': set(["No Effect"])}

		for x in effects:
			data = x.split('|')
			eff = data[1]
			imp = data[2]

			if impact == imp:
				gene = data[3]
				genes.add(gene)

				genome_id = SNP.objects.values_list('result__genome__genome_id', flat=True).filter(snp_position=pos, chromosome__chromosome_name=chrom, library__library_code__in=libraries)[0]

				try:
					product = Feature.objects.values_list('geneproduct', flat=True).filter(geneid=gene, featuretype='gene', genome_id=genome_id)[0]
				except IndexError:
					product = gene

				try:
					wt_allele = SNP.objects.filter(chromosome__chromosome_name__startswith=chrom,
					                               snp_position=pos, library__library_code=wt).values_list('alt_base', flat=True)[0]
				except IndexError:
					wt_allele = "Ref"

				try:
					fmin = Feature.objects.values_list('fmin', flat=True).filter(geneid=gene, featuretype='CDS')[0]
					fmax = Feature.objects.values_list('fmax', flat=True).filter(geneid=gene, featuretype='CDS')[0]
				except IndexError:
					try:
						fmin = Feature.objects.filter(geneid=gene).filter(featuretype='gene').values_list('fmin', flat=True)[0]
						fmax = Feature.objects.filter(geneid=gene).filter(featuretype='gene').values_list('fmax', flat=True)[0]
					except IndexError:
						fmin = 0
						fmax = 0

				snp['effect'].add(eff)
				bp_from_start = pos - fmin
				aa_from_start = int(ceil(bp_from_start/3))
				gene_length = int(ceil((fmax-fmin)/3))

				#Adds all alternate and references alleles
				for lib in group_libs:
					if record.genotype(sample).gt_type == 1:
						hetero = True

					if hetero:
						lib_dict[lib]['alt'].update([alt, "Ref"])

					elif alt:
						lib_dict[lib]['alt'].update([alt])
						lib_dict[lib]['effect'] = set(eff)

		if pos not in snp_dict:
			snp = add_values_to_empty_dictionary(snp, record, alt, lib_dict, gene_length, impact, genes, wt_allele, product, aa_from_start, fmin, fmax)
			snp_dict[pos] = dict(snp)

		#Appends values that are not present in the dictionary
		else:
			snp_dict[pos]['quality'].add(qual)
			snp_dict[pos]['gene'].add(genes)
			snp_dict[pos]['impact'].add(impact)
			snp_dict[pos]['effect'].add(eff)
			snp_dict[pos]['wt_allele'].add(wt_allele)
			snp_dict[pos]['product'].add(product)
			snp_dict[pos]['aa_from_start'].add(aa_from_start)
			snp_dict[pos]['gene_length'].add(gene_length)

			if alt not in snp_dict[pos]['alt']:
				for lib in group_libs:
					if record.genotype(sample).gt_type == 1:
						hetero = True

					if hetero:
						lib_dict[lib]['alt'].update([alt, "Ref"])

					elif alt:
						lib_dict[lib]['alt'].update([alt])
						lib_dict[lib]['effect'] = set(eff)


			if ref not in snp_dict[pos]['ref']:
				if 'Ref' in snp_dict[pos]['ref']:
					snp_dict[pos]['ref'] = {ref}
				else:
					snp_dict[pos]['ref'].add(ref)

	return [snp_dict, genome_id]

# Returns the snp that are found from compare_libraries_search. Opens the vcf-contrast file.
def impact_snps(request):

	# Collects all values from the GET request
	analysis_path = request.GET.get('analysis_path')
	group1 = ast.literal_eval(request.GET.get('add'))
	group2 = ast.literal_eval(request.GET.get('neg'))
	wt = request.GET.get('wt')
	libraries = group1 + group2
	impact = request.GET.get('impact')
	order_by = request.GET.get('order_by', 'quality')
	s = request.GET.get('s')
	att = request.GET.get('att')
	high_ct = request.GET.get('high_ct')
	moderate_ct = request.GET.get('moderate_ct')
	low_ct = request.GET.get('low_ct')

	group1.sort()
	group2.sort()

	result_path_0 = os.path.join(analysis_path, '0000.vcf')
	result_path_1 = os.path.join(analysis_path, '0001.vcf')
	output_path_0 = os.path.join(analysis_path, '%s_impact_0000.vcf' % impact)
	output_path_1 = os.path.join(analysis_path, '%s_impact_0001.vcf' % impact)

	#If output file has not been created
	if not os.path.isfile(output_path_1):

		#If no specific sort is required
		if not s:
			cmd = """cat %s| java -jar /usr/local/snpEff/SnpSift.jar filter "( ANN[*].IMPACT = '%s')" > %s """
			subprocess.call(cmd % (result_path_0, impact, output_path_0), shell=True, stdout=subprocess.PIPE)
			subprocess.call(cmd % (result_path_1, impact, output_path_1), shell=True, stdout=subprocess.PIPE)

		#Sorts results by specified value
		else:
			if att == "0":
				s = int(s)
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar filter "(ANN[*].IMPACT = '%s') & (POS = %d)" | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar extractFields - POS REF ALT CHROM ANN[*].GENE ANN[*].EFFECT QUAL ANN[*].AA"""
			elif att == "ref":
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar filter "(ANN[*].IMPACT = '%s') & (REF = '%s')" | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar extractFields - POS REF ALT CHROM ANN[*].GENE ANN[*].EFFECT QUAL ANN[*].AA"""
			elif att == "alt":
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar filter "(ANN[*].IMPACT = '%s') & (ALT = '%s')" | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar extractFields - POS REF ALT CHROM ANN[*].GENE ANN[*].EFFECT QUAL ANN[*].AA"""
			elif att == "quality":
				s = int(s)
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar filter "(ANN[*].IMPACT = '%s') & (QUAL = %d)" | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar extractFields - POS REF ALT CHROM ANN[*].GENE ANN[*].EFFECT QUAL ANN[*].AA"""
			elif att == "chromosome":
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar filter "(ANN[*].IMPACT = '%s') & (CHROM =~ '%s')" | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar extractFields - POS REF ALT CHROM ANN[*].GENE ANN[*].EFFECT QUAL ANN[*].AA"""
			elif att == "impact":
				s = s.replace(' ', '_').upper()
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar filter "(ANN[*].IMPACT = '%s') & (ANN[*].EFFECT = '%s')" | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar extractFields - POS REF ALT CHROM ANN[*].GENE ANN[*].EFFECT QUAL ANN[*].AA"""
			elif att == "gene":
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar filter "(ANN[*].IMPACT = '%s') & (ANN[*].GENE = '%s')" | java -jar /usr/local/Cellar/snpeff/3.6c/libexec/SnpSift.jar extractFields - POS REF ALT CHROM ANN[*].GENE ANN[*].EFFECT QUAL ANN[*].AA"""

			subprocess.call(cmd % (result_path_0, impact, output_path_0, s), shell=True, stdout=subprocess.PIPE)
			subprocess.call(cmd % (result_path_1, impact, output_path_1, s), shell=True, stdout=subprocess.PIPE)

	snp_dict = defaultdict(dict)

	snp_dicts = add_snps_from_vcf(output_path_0, libraries, group1, snp_dict, wt, impact)
	snp_dicts = add_snps_from_vcf(output_path_1, libraries, group2, snp_dicts[0], wt, impact)

	genome_id = snp_dicts[1]

	test_dict = dict(snp_dict)
	if order_by == '0':
		sorted_snp = sorted(test_dict.iteritems())
	elif order_by == 'quality':
		sorted_snp = sorted(test_dict.iteritems(), key=lambda (k, v): v[order_by], reverse=True)
	else:
		sorted_snp = sorted(test_dict.iteritems(), key=lambda (k, v): v[order_by])

	count = len(snp_dict)
	paginator = Paginator(sorted_snp, 200)
	page = request.GET.get('page')

	# Calls utils method to append new filters or order_by to the current url
	filter_urls = build_orderby_urls(request.get_full_path(), ['chromosome', 'ref', 'quality', 'impact', 'gene',
	                                                           'gene_length', 'aa', 'wt_allele', 'alt', 'group1_consistency', 'group2_consistency'])
	try:
		results = paginator.page(page)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)

	toolbar_max = min(results.number + 4, paginator.num_pages)
	toolbar_min = max(results.number - 4, 0)
	c = {"analysis_path": analysis_path, "paginator": paginator, "results": results, "libraries": libraries, "add": group1,
	     "impact": impact, "neg": group2, "wt": wt, "high_ct": high_ct, "low_ct": low_ct, "moderate_ct":moderate_ct,
	     "filter_urls": filter_urls, "toolbar_max": toolbar_max, "toolbar_min": toolbar_min, "count": count, "genome_id": genome_id}
	return render_to_response('snpdb/impact_snps_search.html', c, context_instance=RequestContext(request))


def add_values_to_empty_dictionary(snp, record, alt, lib_dict, gene_length, impact, genes, wt, product, aa_from_start, fmin, fmax):
	snp['chromosome'] = record.CHROM
	snp['ref'] = {record.REF}
	snp['alt'] = {alt}
	snp['quality'] = {record.QUAL}
	snp['impact'] = {impact}
	snp['gene'] = genes
	snp['wt_allele'] = {wt}
	snp['library_alleles'] = dict(lib_dict)
	snp['product'] = product
	snp['aa_from_start'] = {aa_from_start}
	snp['start'] = fmin
	snp['stop'] = fmax
	snp['gene_length'] = [gene_length]
	return snp


def compare_isec_search(request):
	group1 = request.GET.getlist('check1')
	group2 = request.GET.getlist('check2')
	wt = request.GET.get('wt')

	group1.sort()
	group2.sort()

	#Captures vcf file location
	vcf1 = VCF_Files.objects.values_list('vcf_path', flat=True).filter(library__library_code__in=group1).distinct()
	vcf2 = VCF_Files.objects.values_list('vcf_path', flat=True).filter(library__library_code__in=group2).distinct()

	#Gets path of vcf files.
	direct = os.path.abspath(os.path.dirname(__file__))
	pro_dir = re.findall('(^.*)\/snpdb', direct)[0]
	vcf_path = os.path.join(direct, 'vcf_files')

	group1_path = []
	for each in vcf1:
		vcf1_path = os.path.join(pro_dir, each)
		group1_path.append(vcf1_path)
	group1_path.sort()

	group2_path = []
	for each in vcf2:
		vcf2_path = os.path.join(pro_dir, each)
		group2_path.append(vcf2_path)
	group2_path.sort()

	library_path = group1_path + group2_path
	libs = group1 + group2
	vcf_string = '_'.join(libs)

	#Determines the location of where analysis results will be stored.
	path = os.path.join(vcf_path, 'vcf_isec_%s_%s' % (vcf_string, datetime.datetime.utcnow().strftime("%Y-%m-%d")))

	#Final output paths
	output_path1 = os.path.join(path, "0000.vcf") #contains snps private to group1
	output_path2 = os.path.join(path, "0001.vcf") #contains snps private to group2

	if os.path.isdir(path):
		print "File already present"
		pass
	else:
		os.mkdir(path)
		#Checks to see if files have been zipped and indexed. Bcftools requires indexed vcf files.
		for fname in library_path:
			if os.path.isfile(fname):
				try:
					subprocess.check_call(['bgzip', fname])
					subprocess.check_call(['tabix', '-p', 'vcf', '-f', '%s.gz' % fname])
				except IOError:
					pass
			elif os.path.isfile('%s.gz' % fname):
				subprocess.check_call(['tabix', '-p', 'vcf', '-f', '%s.gz' % fname])
				print "files already zipped"

		#Creates a string of all zipped file in group1 and runs bcftools isec on files in group1
		if len(group1_path) > 1:
			group1_isec = os.path.join(path, "group1.vcf")
			bcftools_isec(group1_path, path, len(group1_path))

			try:
				subprocess.check_call(['bgzip', group1_isec])
				subprocess.check_call(['tabix', '-p', 'vcf', '-f', '%s.gz' % group1_isec])
			except IOError:
				pass
		else:
			group1_isec = group1_path[0]

		#Creates a string of all zipped file in group1 and runs bcftools isec on files in group2
		if len(group2_path) > 1:
			group2_isec = os.path.join(path, "group2.vcf")
			bcftools_isec(group2_path, path, len(group2_path))

			os.rename(os.path.join(path, "0000.vcf"), group2_isec)

			try:
				subprocess.check_call(['bgzip', group2_isec])
				subprocess.check_call(['tabix', '-p', 'vcf', '-f', '%s.gz' % group2_isec])
			except IOError:
				pass
		else:
			group2_isec = group2_path[0]

		#Runs bcftools isec on the previously created isec files
		isec_paths = [group1_isec, group2_isec]


		bcftools_isec(isec_paths, path, 1)

	#Opens the returned vcf-contrast file and counts the data.
	lib_effect = []
	lib_total = 0

	lib_high_effects = defaultdict(int)
	lib_moderate_effects = defaultdict(int)
	lib_modifier_effects = defaultdict(int)
	lib_low_effects = defaultdict(int)

	print "opening vcf-isec"
	vcf_reader1 = vcf.Reader(open('%s' % output_path1, 'r'))
	snp_total_counts = [0, 0, 0, 0, 0]

	for record in vcf_reader1:

		#Keeps track of what effect type each snp has. [high, moderate, low, modifier]
		impact_counts = [0, 0, 0, 0]

		#Places each type of impact into dictionary of the effect. SNPs with multiple impacts
		# will have all impacts accounted for in the impact total.
		# i.e, SNPs with Downstream and Upstream effects will results in an addition to both impact counts.
		effects = record.INFO['ANN']

		for x in effects:
			eff = x.split('|')
			if eff[2] == "HIGH":
				impact_counts[0] += 1
				lib_high_effects[eff[1]] += 1
			elif eff[2] == "MODERATE":
				impact_counts[1] += 1
				lib_moderate_effects[eff[1]] += 1
			elif eff[2] == "LOW":
				impact_counts[2] += 1
				lib_low_effects[eff[1]] += 1
			elif eff[2] == "MODIFIER":
				impact_counts[3] += 1
				lib_modifier_effects[eff[1]] += 1

		# Counts the number of snps effected by each impact type. Snp is only counted once for each impact
		#  i.e. if SNP has two modifying impacts, it is only counted once.

		#Keeps track of the number of snps affected by each impact type: [High, Moderate, Low, Modifier, Total]
		# If an effect is present, add to total snp count
		if sum(impact_counts) > 0:
			snp_total_counts[4] += 1

		if impact_counts[0] > 0:
			snp_total_counts[0] += 1
		if impact_counts[1] > 0:
			snp_total_counts[1] += 1
		if impact_counts[2] > 0:
			snp_total_counts[2] += 1
		if impact_counts[3] > 0:
			snp_total_counts[3] += 1

	vcf_reader2 = vcf.Reader(open('%s' % output_path2, 'r'))
	for record in vcf_reader2:

		#Keeps track of what effect type each snp has. [high, moderate, low, modifier]
		impact_counts = [0, 0, 0, 0]
		
		# Places each type of impact into dictionary of the effect. SNPs with multiple impacts
		# will have all impacts accounted for in the impact total.
		# i.e, SNPs with Downstream and Upstream effects will results in an addition to both impact counts.
		effects = record.INFO['ANN']

		for x in effects:
			eff = x.split('|')
			if eff[2] == "HIGH":
				impact_counts[0] += 1
				lib_high_effects[eff[1]] += 1
			elif eff[2] == "MODERATE":
				impact_counts[1] += 1
				lib_moderate_effects[eff[1]] += 1
			elif eff[2] == "LOW":
				impact_counts[2] += 1
				lib_low_effects[eff[1]] += 1
			elif eff[2] == "MODIFIER":
				impact_counts[3] += 1

		# Counts the number of snps effected by each impact type. Snp is only counted once for each impact
		#  i.e. if SNP has two modifying impacts, it is only counted once.

		#Keeps track of the total library counts: [High, Moderate, Low, Modifier, Consistent, Total]
		if sum(impact_counts) > 0:
			snp_total_counts[4] += 1

		if impact_counts[0] > 0:
			snp_total_counts[0] += 1
		if impact_counts[1] > 0:
			snp_total_counts[1] += 1
		if impact_counts[2] > 0:
			snp_total_counts[2] += 1
		if impact_counts[3] > 0:
			snp_total_counts[3] += 1

	lib_tuple = (dict(lib_high_effects), dict(lib_moderate_effects), dict(lib_low_effects), dict(lib_modifier_effects),
	             snp_total_counts)
	lib_effect.append(lib_tuple)

	return render_to_response('snpdb/compare_libraries_search.html', {"group1": group1,
	                                                        "group2": group2,
	                                                        "wt": wt,
	                                                        "lib_high_effects": dict(lib_high_effects),
	                                                        "lib_moderate_effects": dict(lib_moderate_effects),
	                                                        "lib_modifier_effects": dict(lib_modifier_effects),
	                                                        "lib_low_effects": dict(lib_low_effects),
	                                                        "lib_total_counts": snp_total_counts,
	                                                        "lib_total": lib_total,
	                                                        "lib_effect": lib_effect,
	                                                        "analysis_path": path})

#Runs bcftools isec
def bcftools_isec(library_path, output_dir, number_collapse):
	zip_vcf = ''

	for each in library_path:
		zips = str(each) + '.gz'
		zip_vcf += ' ' + zips

	print zip_vcf

	p = subprocess.Popen(["""bcftools isec -n=%d -p %s -c some %s""" % (number_collapse, output_dir, zip_vcf)], shell=True, stdout=subprocess.PIPE)
	p.communicate()
	p.wait()



#Displays a more in depth view of high and moderate impacts on a specific gene.
def gene_snp_summary(request):
	gene_id = request.GET.get('geneid')
	analysis_path = request.GET.get('analysis_path')
	gene_length = ast.literal_eval(request.GET.get('length'))[0]
	wt = request.GET.get('wt')
	genome_id = request.GET.get('genome_id')

	path_1 = os.path.join(analysis_path, "0000.vcf")
	path_2 = os.path.join(analysis_path, "0001.vcf")

	try:
		product = Feature.objects.values_list('geneproduct', flat=True).filter(geneid=gene_id, featuretype='gene', genome_id=genome_id)[0]
	except IndexError:
		product = "No Gene"

	try:
		fmin = Feature.objects.values_list('fmin', flat=True).filter(geneid=gene_id, featuretype='CDS')[0]
		fmax = Feature.objects.values_list('fmax', flat=True).filter(geneid=gene_id, featuretype='CDS')[0]
	except IndexError:
		try:
			fmin = Feature.objects.filter(geneid=gene_id).filter(featuretype='gene').values_list('fmin', flat=True)[0]
			fmax = Feature.objects.filter(geneid=gene_id).filter(featuretype='gene').values_list('fmax', flat=True)[0]
		except IndexError:
			fmin = 0
			fmax = 0

	snp_list = []

	count_list_1 = get_impact_counts_for_gene(path_1, gene_id, gene_length, snp_list)

	snp_list = count_list_1[0]
	high_ct = count_list_1[1]
	moderate_ct = count_list_1[2]
	low_ct = count_list_1[3]

	count_list_2 = get_impact_counts_for_gene(path_2, gene_id, gene_length, snp_list)

	snp_list = count_list_2[0]
	high_ct += count_list_2[1]
	moderate_ct += count_list_2[2]
	low_ct += count_list_2[3]

	return render_to_response('snpdb/gene_snp_summary.html', {"gene_id": gene_id,
	                                                          "wt": wt,
	                                                          "gene_name": product,
	                                                          "high_ct": high_ct,
	                                                          "moderate_ct": moderate_ct,
	                                                          "low_ct": low_ct,
	                                                          "snp_list": snp_list,
	                                                          "fmin": fmin,
	                                                          "fmax": fmax,
	                                                          }, context_instance=RequestContext(request))


def get_impact_counts_for_gene(filepath, gene_id, gene_length, snp_list):

	cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/snpEff/SnpSift.jar filter "( ANN[*].GENEID = '%s') & ((ANN[*].IMPACT = 'HIGH') | (ANN[*].IMPACT = 'MODERATE'))" | java -jar /usr/local/snpEff/SnpSift.jar extractFields - POS REF ALT CHROM ANN[*].GENEID ANN[*].EFFECT QUAL ANN[*].AA ANN[*].IMPACT"""
	cmd2 = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar /usr/local/snpEff/SnpSift.jar filter "( ANN[*].GENE = '%s') & (ANN[*].IMPACT = 'LOW')" | java -jar /usr/local/snpEff/SnpSift.jar extractFields - POS REF ALT CHROM ANN[*].GENE ANN[*].EFFECT QUAL ANN[*].AA ANN[*].IMPACT"""
	snps = subprocess.Popen(cmd % (filepath, gene_id), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	low_snps = subprocess.Popen(cmd2 % (filepath, gene_id), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	high_ct = 0
	moderate_ct = 0
	low_ct = 0

	for line in snps.stdout:

		snp_info = {}
		if line.startswith('#POS'):
			continue
		else:
			snp = line.split('\t')
			chrom = snp[3].split('_')[0]
			ref = snp[1]
			alt = snp[2]
			gene = snp[4]
			effect_type = snp[5]
			quality = snp[6]
			impact = snp[8]
			aa_change = snp[7]

			aa_pos = re.findall("(\d+)", aa_change)[0]

			if len(ref) > len(alt):
				gain_of_function = "True"
			else:
				gain_of_function = "False"


			snp_info['position'] = snp[0]
			snp_info['ref'] = ref
			snp_info['alt'] = alt
			snp_info['chromosome'] = chrom
			snp_info['gain_of_function'] = gain_of_function
			snp_info['gene'] = gene
			snp_info['impact'] = impact
			snp_info['quality'] = quality
			snp_info['effect'] = effect_type
			snp_info['aa_pos'] = aa_pos
			snp_info['percent_impacted'] = float( (gene_length - float(aa_pos)) / gene_length) * 100

			snp_list.append(snp_info)


			if snp[8].strip() == "HIGH":
				high_ct += 1
			elif snp[8].strip() == "MODERATE":
				moderate_ct += 1

	for line in low_snps.stdout:
		if line.startswith('#POS'):
			pass
		else:
			low_ct += 1

	return [snp_list, high_ct, moderate_ct, low_ct]