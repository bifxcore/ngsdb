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


#Compares multiple libraries by running vcf-contrast. Returns the results and counts the number of snps by impact types
def compare_libs_search(request):
	library_1 = request.GET.getlist('check1')
	library_2 = request.GET.getlist('check2')
	wt = request.GET.get('wt')

	library_1.sort()
	library_2.sort()

	#Captures vcf file location
	vcf1 = VCF_Files.objects.values_list('vcf_path', flat=True).filter(library__library_code__in=library_1).distinct()
	vcf2 = VCF_Files.objects.values_list('vcf_path', flat=True).filter(library__library_code__in=library_2).distinct()

	#Gets path of vcf files.
	direct = os.path.abspath(os.path.dirname(__file__))
	pro_dir = re.findall('(^.*)\/snpdb', direct)[0]
	vcf_path = os.path.join(direct, 'vcf_files')

	#Collects all libraries to be compared.
	group_1_path = []
	for each in vcf1:
		vcf1_path = os.path.join(pro_dir, each)
		group_1_path.append(vcf1_path)
	group_1_path.sort()

	group_2_path = []
	for each in vcf2:
		vcf2_path = os.path.join(pro_dir, each)
		group_2_path.append(vcf2_path)
	group_2_path.sort()

	libraries = group_1_path + group_2_path
	libs = library_1 + library_2
	vcf_string = '_'.join(libs)

	#Determines the location of where analysis results will be stored.
	path = os.path.join(vcf_path, 'vcf_contrast_%s_%s' % (vcf_string, datetime.datetime.utcnow().strftime("%Y-%m-%d")))
	merge_file2 = os.path.join(path, 'merge_contrast.vcf')
	analysis_path = os.path.join('vcf_contrast_%s_%s' % (vcf_string, datetime.datetime.utcnow().strftime("%Y-%m-%d")), 'merge_contrast_replace.vcf')

	#Checks to see if analysis has already been completed. If the analysis files are not present, bcftools is called.
	if os.path.isdir(path):
		print "File already present"
		replace_file = os.path.join(path, 'merge_contrast_replace.vcf')
		pass
	else:
		os.mkdir(path)
		#Checks to see if files have been zipped and indexed. Bcftools requires indexed vcf files.
		for fname in libraries:
			if os.path.isfile(fname):
				# zips and indexes vcf-files for vcf-merge
				try:
					subprocess.check_call(['bgzip', fname])
					subprocess.check_call(['tabix', '-p', 'vcf', '%s.gz' % fname])
				except IOError:
					pass
			elif os.path.isfile('%s.gz' % fname):
				print "files already zipped"

		#Creates a string of all zipped file
		zip_vcf = ''
		for each in libraries:
			zips = str(each) + '.gz'
			zip_vcf = zip_vcf + ' ' + zips

		#Runs the vcf-merge command.
		merge_file = os.path.join(path, 'merge.vcf')

		p = subprocess.Popen(["""bcftools merge -m none --force-samples %s > %s""" % (zip_vcf, merge_file)], shell=True, stdout=subprocess.PIPE)
		p.communicate()
		print "files merged"

		# #collects all file ids.
		add_code = []
		neg_code = []

		for lib in library_1:
			add_code.append("s" + lib)

		for lib in library_2:
			neg_code.append("s" + lib)

		add1 = '+' + ','.join(add_code)
		neg1 = '-' + ','.join(neg_code)
		add2 = '+' + ','.join(neg_code)
		neg2 = '-' + ','.join(add_code)


		#zips replace file for vcf-contrast
		try:
			subprocess.check_call(['bgzip', merge_file])
			subprocess.check_call(['tabix', '-p', 'vcf', '%s.gz' % merge_file])
		except IOError:
			pass

		# print "calling vcf-contrast"
		zip_replace = merge_file + '.gz'
		vcf_contrast1 = os.path.join(path, 'vcf_contrast_1.vcf')
		vcf_contrast2 = os.path.join(path, 'vcf_contrast_2.vcf')

		p = subprocess.Popen(["""vcf-contrast -n %s %s %s > %s""" % (add1, neg1, zip_replace, vcf_contrast1)], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
		p.communicate()
		p = subprocess.Popen(["""vcf-contrast -n %s %s %s > %s""" % (add2, neg2, zip_replace, vcf_contrast2)], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
		p.communicate()

		#zips replace file for vcf-contrast
		try:
			subprocess.check_call(['bgzip', vcf_contrast1])
			subprocess.check_call(['tabix', '-p', 'vcf', '%s.gz' % vcf_contrast1])
			subprocess.check_call(['bgzip', vcf_contrast2])
			subprocess.check_call(['tabix', '-p', 'vcf', '%s.gz' % vcf_contrast2])
		except IOError:
			pass

		#merging vcf_contrast files
		p = subprocess.Popen(["""bcftools merge --force-samples -m none %s.gz %s.gz > %s""" % (vcf_contrast1, vcf_contrast2, merge_file2)], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
		p.communicate()
		print "files merged"

		# Replaces all missing genotypes with wildtype genotypes
		replace_file = os.path.join(path, 'merge_contrast_replace.vcf')
		p = subprocess.Popen(["""bcftools +missing2ref %s > %s """ % (merge_file2, replace_file)], stdout=subprocess.PIPE, shell=True)
		p.communicate()

	#Opens the returned vcf-contrast file and counts the data.
	print "opening vcf-contrast"
	lib_effect = []
	lib_total = 0

	vcf_reader = vcf.Reader(open('%s' % replace_file, 'r'))
	date = datetime.datetime.utcnow().strftime("%Y-%m-%d").replace('-', '')
	source = 'source_' + date + '.1'
	cmd = vcf_reader.metadata[source][0]

	group1 = re.findall('\+(.*) \-', cmd)[0].split(',')
	group2 = re.findall('\+.* \-(.*) ', cmd)[0].split(',')

	lib_high_effects = defaultdict(int)
	lib_moderate_effects = defaultdict(int)
	lib_modifier_effects = defaultdict(int)
	lib_low_effects = defaultdict(int)

	#Keeps track of the total library counts: [High, Moderate, Low, Modifier, Consistent, Total]
	lib_total_counts = [0, 0, 0, 0, 0, 0, '']

	# equivalent_gts = ['0/1', '1/1']
	for record in vcf_reader:
		for lib in libs:
			# print lib.encode("utf8")
			alt_lib = "2:s" + lib.encode("utf8")
			gt = [record.genotype("s" + lib.encode("utf8")).gt_type, record.genotype(alt_lib).gt_type]

			group1_gt = set()
			group2_gt = set()
			alt = ','.join(str(i) for i in record.ALT)

			if len(group1) > 1:
				for each in gt:
					if each == 0:
						group1_gt.add("Ref")
					if each == 1:
						group1_gt.add(alt)
						group1_gt.add("Ref")
					if each == 2:
						group1_gt.add(alt)
			group1_eq = check_equal(group1_gt, alt)

			if len(group2) > 1:
				for each in gt:
					if each == 0:
						group2_gt.add("Ref")
					if each == 1:
						group2_gt.add(alt)
						group2_gt.add("Ref")
					if each == 2:
						group2_gt.add(alt)
			group2_eq = check_equal(group2_gt, alt)

		#Keeps track of what effect type each snp has. [high, moderate, low, modifier]
		lib_impact_counts = [0, 0, 0, 0]

		#Places each type of impact into dictionary of the effect. SNPs with multiple impacts
		# will have all impacts accounted for in the impact total.
		# i.e, SNPs with Downstream and Upstream effects will results in an addition to both impact counts.
		effects = record.INFO['ANN']

		high_eq = 0
		moderate_eq = 0
		low_eq = 0
		modifier_eq = 0

		for x in effects:
			eff = x.split('|')
			if eff[2] == "HIGH":
				lib_impact_counts[0] += 1
				lib_high_effects[eff[1]] += 1
				if group1_eq or group2_eq:
					high_eq += 1
			elif eff[2] == "MODERATE":
				lib_impact_counts[1] += 1
				lib_moderate_effects[eff[1]] += 1
				if group1_eq or group2_eq:
					moderate_eq += 1
			elif eff[2] == "LOW":
				lib_impact_counts[2] += 1
				lib_low_effects[eff[1]] += 1
				if group1_eq or group2_eq:
					low_eq += 1
			elif eff[2] == "MODIFIER":
				lib_impact_counts[3] += 1
				lib_modifier_effects[eff[1]] += 1
				if group1_eq or group2_eq:
					modifier_eq += 1

		if high_eq > 0:
			lib_high_effects["Equivalent SNPs"] += 1
		if moderate_eq > 0:
			lib_moderate_effects["Equivalent SNPs"] += 1
		if low_eq > 0:
			lib_low_effects["Equivalent SNPs"] += 1
		if modifier_eq > 0:
			lib_modifier_effects["Equivalent SNPs"] += 1

		# Counts the number of snps effected by each impact type. Snp is only counted once for each impact
		#  i.e. if SNP has two modifying impacts, it is only counted once.

		if sum(lib_impact_counts) > 0:
			lib_total_counts[5] = group1
			lib_total_counts[4] += 1

		if lib_impact_counts[0] > 0:
			lib_total_counts[0] += 1
		if lib_impact_counts[1] > 0:
			lib_total_counts[1] += 1
		if lib_impact_counts[2] > 0:
			lib_total_counts[2] += 1
		if lib_impact_counts[3] > 0:
			lib_total_counts[3] += 1

	lib_tuple = (dict(lib_high_effects), dict(lib_moderate_effects), dict(lib_low_effects), dict(lib_modifier_effects), lib_total_counts)
	lib_effect.append(lib_tuple)
	lib_total += lib_total_counts[4]

	return render_to_response('snpdb/compare_libraries_search.html', {"library1": library_1,
	                                                        "library2": library_2,
	                                                        "wt": wt,
	                                                        "lib1_high_effects": dict(lib_high_effects),
	                                                        "lib1_moderate_effects": dict(lib_moderate_effects),
	                                                        "lib1_modifier_effects": dict(lib_modifier_effects),
	                                                        "lib1_low_effects": dict(lib_low_effects),
	                                                        "lib1_total_counts": lib_total_counts,
	                                                        "lib1_total": lib_total,
	                                                        "lib1_effect": lib_effect,
	                                                        "add_code": group1,
	                                                        "neg_code": group2,
	                                                        "analysis_path": analysis_path})


# Returns the snp that are found from compare_libraries_search. Opens the vcf-contrast file.
def impact_snps(request):

	# Collects all values from the GET request
	analysis_path = request.GET.get('analysis_path')
	add = ast.literal_eval(request.GET.get('add'))
	neg = ast.literal_eval(request.GET.get('neg'))
	wt = request.GET.get('wt')
	libraries = add + neg
	impact = request.GET.get('impact')
	order_by = request.GET.get('order_by', 'quality')
	s = request.GET.get('s')
	att = request.GET.get('att')
	high_ct = request.GET.get('high_ct')
	moderate_ct = request.GET.get('moderate_ct')
	low_ct = request.GET.get('low_ct')
	consistent = request.GET.get('consistent')

	add.sort()
	neg.sort()

	direct = os.path.abspath(os.path.dirname(__file__))
	vcf_path = os.path.join(direct, 'vcf_files')
	path = os.path.join(vcf_path, analysis_path)
	analysis_folder = os.path.join(vcf_path, analysis_path.split('/')[0])
	output_path = os.path.join(analysis_folder, '%s_impact.vcf' % impact)

	#If output file has not been created
	if not os.path.isfile(output_path):

		#If no specific sort is required
		if not s:
			cmd = """cat %s | java -jar /usr/local/snpEff/SnpSift.jar filter "( ANN[*].IMPACT = '%s')" > %s """
			subprocess.call(cmd % (path, impact, output_path), shell=True, stdout=subprocess.PIPE)

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
			subprocess.Popen(cmd % (path, impact, s), shell=True, stdout=subprocess.PIPE)

	snp_dict = defaultdict(dict)
	vcf_reader = vcf.Reader(open(output_path, 'r'))

	for record in vcf_reader:
		snp = defaultdict(set)
		pos = record.POS
		qual = record.QUAL
		chrom = record.CHROM
		effects = record.INFO['ANN']
		alt = ','.join(str(i) for i in record.ALT)
		ref = record.REF
		genes = set()

		lib_dict = {}
		for lib in libraries:
			lib_dict[lib] = {'ref': {"No Snp"}, 'alt': {"No Snp"}, 'effect': {"No Effect"}}

		for x in effects:
			data = x.split('|')
			eff = data[1]
			imp = data[2]

			if impact == imp:
				gene = data[3]
				genes.add(gene)
				# aa_change = effs[7]

				try:
					product = Feature.objects.values_list('geneproduct', flat=True).filter(geneid=gene, featuretype='gene')[0]
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
				for lib in libraries:
					alt_lib = "2:" + lib
					gt = [record.genotype(lib).gt_type, record.genotype(alt_lib).gt_type]

					for each in gt:
						if 'No Snp' in lib_dict[lib]['alt']:
							if each == 0:
								lib_dict[lib]['alt'] = {"Ref"}
							if each == 1:
								lib_dict[lib]['alt'] = {alt}
								lib_dict[lib]['alt'].add("Ref")
							if each == 2:
								lib_dict[lib]['alt'] = {alt}
							lib_dict[lib]['effect'] = {eff}
						else:
							if each == 0:
								lib_dict[lib]['alt'].add("Ref")
							if each == 1:
								lib_dict[lib]['alt'].add(alt)
								lib_dict[lib]['alt'].add("Ref")
							if each == 2:
								lib_dict[lib]['alt'].add(alt)

		#Collects whether the libraries are consistent in snps
		add_gt = []
		if len(add) > 1:
			for each in add:
				gt = lib_dict[each]['alt']
				add_gt.append(gt)
			snp['group1_consistency'] = check_equal(add_gt, alt)
		else:
			snp['group1_consistency'] = True

		neg_gt = []
		if len(neg) > 1:
			for each in neg:
				gt = lib_dict[each]['alt']
				neg_gt.append(gt)
			snp['group2_consistency'] = check_equal(neg_gt, alt)
		else:
			snp['group2_consistency'] = True

		if pos not in snp_dict:
			snp = add_values_to_empty_dictionary(snp, record, alt, lib_dict, gene_length, impact, genes, wt_allele, product, aa_from_start, fmin, fmax)

			if consistent == "on":
				if snp['group1_consistency'] or snp['group2_consistency']:
					snp_dict[pos] = dict(snp)
				else:
					pass
			else:
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
				for lib in libraries:
					gt = record.genotype(lib).gt_bases
					if 'Ref' in lib_dict[lib]['alt']:
						if gt == 0:
							snp_dict[pos]['library_alleles'][lib]['alt'] = {"Ref"}
						if gt == 1:
							snp_dict[pos]['library_alleles'][lib]['alt'] = {alt}
							snp_dict[pos]['library_alleles'][lib]['alt'].add("Ref")
						if gt == 2:
							snp_dict[pos]['library_alleles'][lib]['alt'] = {alt}
						lib_dict[lib]['effect'] = {eff}
					else:
						if gt == 0:
							lib_dict[lib]['alt'].add("Ref")
						if gt == 1:
							snp_dict[pos]['library_alleles'][lib]['alt'].add(alt)
							snp_dict[pos]['library_alleles'][lib]['alt'].add("Ref")
						if gt == 2:
							snp_dict[pos]['library_alleles'][lib]['alt'].add(alt)

			if ref not in snp_dict[pos]['ref']:
				if 'Ref' in snp_dict[pos]['ref']:
					snp_dict[pos]['ref'] = {ref}
				else:
					snp_dict[pos]['ref'].add(ref)

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
	c = {"analysis_path": analysis_path, "paginator": paginator, "results": results, "libraries": libraries, "add": add,
	     "impact": impact, "neg": neg, "wt": wt, "high_ct": high_ct, "low_ct": low_ct, "moderate_ct":moderate_ct,
	     "filter_urls": filter_urls, "toolbar_max": toolbar_max, "toolbar_min": toolbar_min, "count": count}
	return render_to_response('snpdb/impact_snps_search.html', c, context_instance=RequestContext(request))


# Checks if values in list are equal. Used to find snp equivalence.
def check_equal(gt_list, alt):
	wt_eq = True
	alt_eq = True
	for sublist in gt_list:
		if "Ref" not in sublist:
			wt_eq = False
		if alt not in sublist:
			alt_eq = False

	if wt_eq:
		return True
	elif alt_eq:
		return True
	return False
def check_equal(gt_list, alt):
	wt_eq = True
	alt_eq = True
	for sublist in gt_list:
		if "Ref" not in sublist:
			wt_eq = False
		if alt not in sublist:
			alt_eq = False

	if wt_eq:
		return True
	elif alt_eq:
		return True
	return False



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
	snp['gene_length'] = {gene_length}
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
			group1_isec = group1_path


		#Creates a string of all zipped file in group1 and runs bcftools isec on files in group2
		if len(group2_path) > 1:
			group2_isec = os.path.join(path, "group2.vcf")
			bcftools_isec(group2_path, path, len(group2_path))

			os.file.rename

			try:
				subprocess.check_call(['bgzip', group2_isec])
				subprocess.check_call(['tabix', '-p', 'vcf', '-f', '%s.gz' % group2_isec])
			except IOError:
				pass
		else:
			group2_isec = group2_path

		#Runs bcftools isec on the previously created isec files
		isec_paths = group1_isec + " " + group2_isec
		output_path1 = os.path.join(path, "0000.vcf") #contains snps private to group1
		output_path2 = os.path.join(path, "0001.vcf") #contains snps private to group2

		bcftools_isec(isec_paths, path, 1)

	#Opens the returned vcf-contrast file and counts the data.
	print "opening vcf-isec"
	lib_effect = []
	lib_total = 0

	lib_high_effects = defaultdict(int)
	lib_moderate_effects = defaultdict(int)
	lib_modifier_effects = defaultdict(int)
	lib_low_effects = defaultdict(int)


	vcf_reader1 = vcf.Reader(open('%s' % output_path1, 'r'))
	for record in vcf_reader1:

		#Keeps track of what effect type each snp has. [high, moderate, low, modifier]
		lib_impact_counts = [0, 0, 0, 0]

		#Places each type of impact into dictionary of the effect. SNPs with multiple impacts
		# will have all impacts accounted for in the impact total.
		# i.e, SNPs with Downstream and Upstream effects will results in an addition to both impact counts.
		effects = record.INFO['ANN']

		high_eq = 0
		moderate_eq = 0
		low_eq = 0
		modifier_eq = 0

		for x in effects:
			eff = x.split('|')
			if eff[2] == "HIGH":
				lib_impact_counts[0] += 1
				lib_high_effects[eff[1]] += 1
			elif eff[2] == "MODERATE":
				lib_impact_counts[1] += 1
				lib_moderate_effects[eff[1]] += 1
			elif eff[2] == "LOW":
				lib_impact_counts[2] += 1
				lib_low_effects[eff[1]] += 1
			elif eff[2] == "MODIFIER":
				lib_impact_counts[3] += 1
				lib_modifier_effects[eff[1]] += 1

		if high_eq > 0:
			lib_high_effects["Equivalent SNPs"] += 1
		if moderate_eq > 0:
			lib_moderate_effects["Equivalent SNPs"] += 1
		if low_eq > 0:
			lib_low_effects["Equivalent SNPs"] += 1
		if modifier_eq > 0:
			lib_modifier_effects["Equivalent SNPs"] += 1

		# Counts the number of snps effected by each impact type. Snp is only counted once for each impact
		#  i.e. if SNP has two modifying impacts, it is only counted once.

		#Keeps track of the total library counts: [High, Moderate, Low, Modifier, Consistent, Total]
		lib_total_counts = [0, 0, 0, 0, 0, 0, '']
		if sum(lib_impact_counts) > 0:
			lib_total_counts[5] = group1
			lib_total_counts[4] += 1

		if lib_impact_counts[0] > 0:
			lib_total_counts[0] += 1
		if lib_impact_counts[1] > 0:
			lib_total_counts[1] += 1
		if lib_impact_counts[2] > 0:
			lib_total_counts[2] += 1
		if lib_impact_counts[3] > 0:
			lib_total_counts[3] += 1

	# lib_tuple = (dict(lib_high_effects), dict(lib_moderate_effects), dict(lib_low_effects), dict(lib_modifier_effects), lib_total_counts)
	# lib_effect.append(lib_tuple)
	lib_total += lib_total_counts[4]

	vcf_reader2 = vcf.Reader(open('%s' % output_path2, 'r'))
	for record in vcf_reader2:

		# Places each type of impact into dictionary of the effect. SNPs with multiple impacts
		# will have all impacts accounted for in the impact total.
		# i.e, SNPs with Downstream and Upstream effects will results in an addition to both impact counts.
		effects = record.INFO['ANN']

		high_eq = 0
		moderate_eq = 0
		low_eq = 0
		modifier_eq = 0

		for x in effects:
			eff = x.split('|')
			if eff[2] == "HIGH":
				lib_impact_counts[0] += 1
				lib_high_effects[eff[1]] += 1
			elif eff[2] == "MODERATE":
				lib_impact_counts[1] += 1
				lib_moderate_effects[eff[1]] += 1
			elif eff[2] == "LOW":
				lib_impact_counts[2] += 1
				lib_low_effects[eff[1]] += 1
			elif eff[2] == "MODIFIER":
				lib_impact_counts[3] += 1
				lib_modifier_effects[eff[1]] += 1

		if high_eq > 0:
			lib_high_effects["Equivalent SNPs"] += 1
		if moderate_eq > 0:
			lib_moderate_effects["Equivalent SNPs"] += 1
		if low_eq > 0:
			lib_low_effects["Equivalent SNPs"] += 1
		if modifier_eq > 0:
			lib_modifier_effects["Equivalent SNPs"] += 1

		# Counts the number of snps effected by each impact type. Snp is only counted once for each impact
		#  i.e. if SNP has two modifying impacts, it is only counted once.

		#Keeps track of the total library counts: [High, Moderate, Low, Modifier, Consistent, Total]
		if sum(lib_impact_counts) > 0:
			lib_total_counts[5] = group1
			lib_total_counts[4] += 1

		if lib_impact_counts[0] > 0:
			lib_total_counts[0] += 1
		if lib_impact_counts[1] > 0:
			lib_total_counts[1] += 1
		if lib_impact_counts[2] > 0:
			lib_total_counts[2] += 1
		if lib_impact_counts[3] > 0:
			lib_total_counts[3] += 1

	lib_tuple = (dict(lib_high_effects), dict(lib_moderate_effects), dict(lib_low_effects), dict(lib_modifier_effects), lib_total_counts)
	lib_effect.append(lib_tuple)
	lib_total += lib_total_counts[4]

	return render_to_response('snpdb/compare_libraries_search.html', {"library1": group1,
	                                                        "library2": group2,
	                                                        "wt": wt,
	                                                        "lib1_high_effects": dict(lib_high_effects),
	                                                        "lib1_moderate_effects": dict(lib_moderate_effects),
	                                                        "lib1_modifier_effects": dict(lib_modifier_effects),
	                                                        "lib1_low_effects": dict(lib_low_effects),
	                                                        "lib1_total_counts": lib_total_counts,
	                                                        "lib1_total": lib_total,
	                                                        "lib1_effect": lib_effect,
	                                                        "add_code": group1,
	                                                        "neg_code": group2,
	                                                        "analysis_path": path})




#Runs bcftools isec
def bcftools_isec(library_path, output_dir, number_collapse):
	zip_vcf = ''

	for each in library_path:
		zips = str(each) + '.gz'
		zip_vcf += ' ' + zips

	p = subprocess.Popen(["""bcftools isec -n=%d -p %s -c some %s""" % (number_collapse, output_dir, zip_vcf)], shell=True, stdout=subprocess.PIPE)
	p.communicate()
	p.wait()
