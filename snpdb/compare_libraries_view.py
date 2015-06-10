__author__ = 'mcobb'
from snpdb.models import *
from samples.models import *
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from utils import build_orderby_urls
from collections import *
from math import ceil
import subprocess
import datetime
import os
import vcf
import ast
from ngsdbview.viewtools import *
from collections import defaultdict
import numpy
from django.conf import settings
from bokeh.charts import Bar
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.models import NumeralTickFormatter, HoverTool, BoxZoomTool, ResetTool, PanTool, PreviewSaveTool, Range1d, glyphs
from bokeh.models.glyphs import Text
import json


# Displays the search page to compare two groups of libraries for unique and similar snps.
def compare_libs(request):
	ref_genome = request.GET.get('ref_genome')
	if ref_genome:
		lib_list = Library.objects.values('library_code',
		                                  'result__genome__organism__organismcode').filter(result__genome__organism__organismcode=ref_genome).distinct().order_by('library_code')
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
	                                                           "toolbar_min": toolbar_min},
	                          context_instance=RequestContext(request))


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


		genome_id = SNP.objects.values_list('result__genome__genome_id', flat=True).filter(snp_position=pos,
		                                                                                   chromosome__chromosome_name=chrom,
		                                                                                   library__library_code__in=libraries)[0]

		try:
			wt_allele = SNP.objects.filter(chromosome__chromosome_name__startswith=chrom,
			                               snp_position=pos,
			                               library__library_code=wt).values_list('alt_base', flat=True)[0]
		except IndexError:
			wt_allele = "Ref"


		lib_dict = {}
		cnvs = CNV.objects.values('cnv_value', 'library__library_code',
		                          'start', 'stop').distinct().filter(library__library_code__in=libraries,
		                                                             start__lte=pos,
		                                                             stop__gte=pos,
		                                                             chromosome__chromosome_name=chrom)

		for each in cnvs:
			if each['library__library_code'] in group_libs:
				lib_dict[each['library__library_code']] = {'ref': set(), 'alt': set(), 'effect': set(), 'cnv': each['cnv_value']}
			else:
				lib_dict[each['library__library_code']] = {'ref': set(["Ref"]), 'alt': set(["Ref"]), 'effect': set(["No Effect"]), 'cnv': each['cnv_value']}

		for x in effects:
			data = x.split('|')
			eff = data[1]
			imp = data[2]

			if impact == imp:
				gene = data[3]
				genes.add(gene)

				try:
					product = Feature.objects.values_list('geneproduct', flat=True).filter(geneid=gene,
					                                                                       featuretype='gene',
					                                                                       genome_id=genome_id)[0].encode("UTF8")
				except IndexError:
					product = gene.encode("UTF8")


				try:
					gene_pos = Feature.objects.values('fmin', 'fmax').filter(geneid=gene, featuretype='CDS')[0]
					fmin = gene_pos['fmin']
					fmax = gene_pos['fmax']
				except IndexError:
					try:
						gene_pos = Feature.objects.filter(geneid=gene).filter(featuretype='gene').values('fmin', 'fmax')[0]
						fmin = gene_pos['fmin']
						fmax = gene_pos['fmax']
					except IndexError:
						fmin = 0
						fmax = 0

				bp_from_start = pos - fmin
				aa_from_start = int(ceil(bp_from_start/3))
				gene_length = int(ceil((fmax-fmin)/3))

				snp['effect'].add(eff)


				#Adds all alternate and references alleles
				for lib in group_libs:
					if record.genotype(sample).gt_type == 1:
						hetero = True

					if hetero:
						lib_dict[lib]['alt'].update([alt, "Ref"])

					elif alt:
						lib_dict[lib]['alt'].update([alt])
						lib_dict[lib]['effect'] = set([eff])

		if pos not in snp_dict:
			snp = add_values_to_empty_dictionary(snp, record, alt, lib_dict, gene_length, impact, genes, wt_allele, product, aa_from_start, fmin, fmax)
			snp_dict[pos] = dict(snp)

		#Appends values that are not present in the dictionary
		else:
			snp_dict[pos]['quality'].add(qual)
			snp_dict[pos]['gene'].update(genes)
			snp_dict[pos]['impact'].add(impact)
			snp_dict[pos]['effect'].add(eff)
			snp_dict[pos]['wt_allele'].add(wt_allele)
			snp_dict[pos]['product'].add(product.encode("UTF8"))
			snp_dict[pos]['aa_from_start'].add(aa_from_start)
			snp_dict[pos]['gene_length'].append(gene_length)

			if alt not in snp_dict[pos]['alt']:
				for lib in group_libs:
					if record.genotype(sample).gt_type == 1:
						hetero = True

					if hetero:
						lib_dict[lib]['alt'].update([alt, "Ref"])

					elif alt:
						lib_dict[lib]['alt'].update([alt])
						lib_dict[lib]['effect'] = set([eff])


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
	order_by = request.GET.get('order_by', 'chromosome')
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

	java_jar = settings.SNPEFF_JAR_PATH
	print java_jar

	#If output file has not been created
	if not os.path.isfile(output_path_1):

		#If no specific sort is required
		if not s:
			cmd = """cat %s| java -jar %s "( ANN[*].IMPACT = '%s')" > %s """

			subprocess.call(cmd % (result_path_0, java_jar, impact, output_path_0), shell=True, stdout=subprocess.PIPE)
			subprocess.call(cmd % (result_path_1, java_jar, impact, output_path_1), shell=True, stdout=subprocess.PIPE)

		#Sorts results by specified value
		else:

			print "In else statement"
			if att == "0":
				s = int(s)
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar %s "(ANN[*].IMPACT = '%s') & (POS = %d)" """
			elif att == "ref":
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar %s "(ANN[*].IMPACT = '%s') & (REF = '%s')" """
			elif att == "alt":
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar %s "(ANN[*].IMPACT = '%s') & (ALT = '%s')" """
			elif att == "quality":
				s = int(s)
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar %s "(ANN[*].IMPACT = '%s') & (QUAL = %d)" """
			elif att == "chromosome":
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar %s "(ANN[*].IMPACT = '%s') & (CHROM =~ '%s')" """
			elif att == "impact":
				s = s.replace(' ', '_').upper()
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar %s "(ANN[*].IMPACT = '%s') & (ANN[*].EFFECT = '%s')" """
			elif att == "gene":
				cmd = """cat %s | /usr/local/snpEff/scripts/vcfEffOnePerLine.pl | java -jar %s "(ANN[*].IMPACT = '%s') & (ANN[*].GENE = '%s')" """

			subprocess.call(cmd % (result_path_0, java_jar,  impact, output_path_0, s), shell=True, stdout=subprocess.PIPE)
			subprocess.call(cmd % (result_path_1, java_jar, impact, output_path_1, s), shell=True, stdout=subprocess.PIPE)

	snp_dict = defaultdict(dict)

	snp_dicts = add_snps_from_vcf(output_path_0, libraries, group1, snp_dict, wt, impact)
	snp_dicts = add_snps_from_vcf(output_path_1, libraries, group2, snp_dicts[0], wt, impact)

	genome_id = snp_dicts[1]

	test_dict = dict(snp_dict)
	if order_by == '0':
		sorted_snp = sorted(test_dict.iteritems())
	elif order_by == 'quality':
		sorted_snp = sorted(test_dict.iteritems(), key=lambda (k, d): (d['chromosome'], k, ))
	else:
		sorted_snp = sorted(test_dict.iteritems(), key=lambda (k, d): (d['chromosome'], k, ))

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
	snp['product'] = {product}
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
			group1_folder = os.path.join(path, "%s" % '_'.join(group1))
			group1_isec = os.path.join(group1_folder, "0000.vcf")
			bcftools_isec(group1_path, group1_folder, len(group1_path))

			try:
				subprocess.check_call(['bgzip', group1_isec])
				subprocess.check_call(['tabix', '-p', 'vcf', '-f', '%s.gz' % group1_isec])
			except IOError:
				pass

		else:
			group1_isec = group1_path[0]

		#Creates a string of all zipped file in group1 and runs bcftools isec on files in group2
		if len(group2_path) > 1:
			group2_folder = os.path.join(path, "%s" % '_'.join(group2))
			group2_isec = os.path.join(group2_folder, "0000.vcf")
			bcftools_isec(group2_path, group2_folder, len(group2_path))

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

		#Keeps track of the total library counts: [High, Moderate, Low, Modifier, Total]
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
	# lib_total = sum(snp_total_counts)

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

	p = subprocess.Popen(["""bcftools isec -n=%d -p %s -c some %s""" % (number_collapse, output_dir, zip_vcf)], shell=True, stdout=subprocess.PIPE)
	p.communicate()
	p.wait()


#Displays a more in depth view of high and moderate impacts on a specific gene.
def gene_snp_summary(request):
	gene_id = request.GET.get('geneid').encode("UTF8")
	gene_length = ast.literal_eval(request.GET.get('length'))[0]
	wt = request.GET.get('wt').encode("UTF8")
	genome_id = request.GET.get('genome_id')
	group1 = ast.literal_eval(request.GET.get('add'))
	group2 = ast.literal_eval(request.GET.get('neg'))

	libraries = group1 + group2
	if wt:
		libraries.append(wt)
	libraries = sorted([x.encode("UTF8") for x in libraries])

	library_id = Library.objects.values_list('id', flat=True).filter(library_code__in=libraries)
	library_id = [id for id in library_id]

	chrom = Feature.objects.values_list('chromosome', flat=True).filter(geneid=gene_id, genome_id=genome_id)[0]

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

	snp_list = {}
	high_ct = 0
	moderate_ct = 0
	low_ct = 0

	snp_list = get_impact_counts_for_gene(gene_id, gene_length, fmin, snp_list, library_id, chrom)

	for key in snp_list:
		impact = snp_list[key]['impact']

		if impact.strip() == "HIGH":
			high_ct += 1
		elif impact.strip() == "MODERATE":
			moderate_ct += 1
		elif impact.strip() == "LOW":
			low_ct += 1

	snp_list = OrderedDict(sorted(snp_list.items()))

	return render_to_response('snpdb/gene_summary.html', {"gene_id": gene_id,
	                                                      "wt": wt,
	                                                      "libraries": libraries,
	                                                      "gene_name": product,
	                                                      "high_ct": high_ct,
	                                                      "moderate_ct": moderate_ct,
	                                                      "low_ct": low_ct,
	                                                      "snp_list": snp_list,
	                                                      "fmin": fmin,
	                                                      "fmax": fmax,
	                                                      "chrom": chrom,
	                                                      }, context_instance=RequestContext(request))


def get_impact_counts_for_gene(gene_id, gene_length, start_pos, snp_info, libraries, chrom):

	library_codes = Library.objects.values('library_code', 'id').filter(id__in=libraries)
	chromosome = Chromosome.objects.values_list('chromosome_id', flat=True).filter(chromosome_name__startswith=chrom)[0]

	somys = {}
	lib_codes = {}
	for lib in library_codes:
		lib_codes[lib['id']] = {'id': lib['id'], 'library_code': lib['library_code'].encode("UTF8")}
		try:
			somy = CNV.objects.values_list('cnv_value', flat=True).filter(library__library_code=lib['library_code'],
			                                                              cnv_type_id=2,
			                                                              chromosome_id=chromosome)[0]
		except IndexError:
			somy = 0
		somys[lib['library_code'].encode("UTF8")] = somy


	query = '''SELECT snpdb_effect.snp_id AS id, effect_class, effect_string, snp_position, ref_base, alt_base,
							   library_id, quality
		FROM snpdb_effect, snpdb_snp
		WHERE snpdb_effect.snp_id IN (SELECT DISTINCT snpdb_snp.snp_id AS snps
  		FROM snpdb_snp, snpdb_effect
		WHERE library_id IN ({})
		AND effect_string=%s
		AND snpdb_snp.snp_id = snpdb_effect.snp_id
		AND effect_id=66)
		AND effect_id = 64
		AND effect_string IN ('HIGH', 'MODERATE', 'LOW')
		AND snpdb_effect.snp_id = snpdb_snp.snp_id ORDER BY snp_position'''.format(','.join(['%s' for x in range(len(libraries))]))

	params = libraries + [gene_id]
	qs = Effect.objects.raw(query, params)

	#Iterates through all of the snps found within the gene and queried libraries.
	for q in qs:
		impact = q.effect_string
		library_code = lib_codes[q.library_id].get('library_code')
		ref = q.ref_base
		alt = q.alt_base
		effect_type = q.effect_class
		quality = q.quality
		pos = q.snp_position
		aa_pos = int(math.ceil((pos - start_pos)/float(3)))
		percent_impact = float((gene_length - float(aa_pos)) / gene_length) * 100

		if len(ref) > len(alt):
			loss_of_function = "Yes"
		else:
			loss_of_function = "No"

		snps = {}

		#initializes all libraries to WT alleles.
		for each in library_codes:
			try:
				cnv = CNV.objects.values_list('cnv_value', flat=True).filter(library__library_code=each['library_code'],
				                                                             start__lte=pos, stop__gte=pos,
				                                                             chromosome_id=chromosome, cnv_type_id=1)[0]
			except IndexError:
				cnv = 0

			if library_code == each['library_code']:
				library = {'ref': ref,
				           'alt': alt,
				           'loss_of_function': loss_of_function,
				           'quality': quality,
				           'cnv': cnv,
				           'somy': somys[each['library_code']]}
			else:
				library = {'ref': ref,
				           'alt': ref,
				           'loss_of_function': "None",
				           'quality': 0,
				           'cnv': cnv,
				           'somy': somys[each['library_code']]}


			if pos in snp_info:
				snp_info[pos][each['library_code']] = library

			else:
				snps['chromosome'] = chromosome
				snps['gene'] = gene_id
				snps['impact'] = impact
				snps['effect'] = [effect_type]
				snps['aa_pos'] = aa_pos
				snps['percent_impacted'] = percent_impact
				snps[each['library_code']] = library
				snp_info[pos] = snps

	return snp_info


def compare_libraries_somy(request, experimentId):
	"""
	Display somy chart(s)
	:param request: libcodes, referencegenome/resultids
	:return: all chart objects
	"""

	kwargs = {}
	#kwargs['user']=user
	kwargs['listoflinks']=listoflinks
	kwargs['title']="Comparing Somy"

	if request.method == 'POST':

		libcodes = request.POST.getlist('libcodes', '')

		color_list = []
		legendvalues = []
		for libcode in libcodes:
			libobj = Library.objects.get(library_code=libcode)
			legendvalues.append(libobj.library_code+'('+libobj.sampleid.samplename+')')
			color = request.POST.get(libcode)
			color_list.append(color)

		somyobjects = CNV.objects.filter(library__library_code__in=libcodes).filter(cnv_type__cvterm='Somy')
		contignames = []
		for contig in sorted(list(set(somyobjects.values_list('chromosome__chromosome_name', flat=True)))):
			contignames.append(re.sub(r'\D+', '', re.sub(r'_.+', '', contig)))

		somy_dict = {}
		max_somy = 0
		for libcode in libcodes:
			somy_for_lib = []
			for somyvalue in somyobjects.filter(library__library_code=libcode).order_by('chromosome__chromosome_name').values_list('cnv_value', flat=True):
				somy_for_lib.append(somyvalue)

				if somyvalue > max_somy:
					max_somy = somyvalue

			somy_dict[libcode] = somy_for_lib


		plot = Bar(somy_dict, cat=contignames, xlabel="Chromosomes", ylabel="Somy Values",
		           width=1000, height=500, palette=color_list, legend=True, tools='hover')

		hover = plot.select(dict(type=HoverTool))
		hover.tooltips = [("Chromosome", "$x"), ("CNV Value", "@y")]


		script, div = components(plot)

		return render_to_response('snpdb/compare_libraries_somy.html', {"script":script, "div":div}, context_instance=RequestContext(request))

	else:
		exp = Experiment.objects.get(id=experimentId)
		kwargs['exp'] = exp
		libs = []
		for sample in exp.samples.all():
			for lib in sample.library_set.all():
				libs.append(lib)

		kwargs['libs'] = libs
		kwargs['display_form'] = 'yes'
		kwargs['colors'] = ['blue', 'orange', 'red', 'green', 'yellow', 'purple', 'pink', 'black', 'gray', 'cyan', 'white']

	return render_to_response('snpdb/compare_libraries_somy.html', kwargs, context_instance=RequestContext(request))


def compare_libraries_cnv_graphs(request):
	data = json.loads(request.body)

	colors = data['colors']
	libcodes = data['libcodes']
	chromosome = data['chromosome']
	linestyles = data['linestyles']

	charts = {}

	graph = figure(x_axis_label='Position (bp)', y_axis_label='CNV Values', title=chromosome,
	               tools=[BoxZoomTool(), PanTool(), HoverTool(tooltips = [("position", "@x"), ("CNV Value", "@y")]),
	                      ResetTool(), PreviewSaveTool()], plot_height=800, plot_width=1300, toolbar_location="left")

	max_cnv = 0

	for x in range(0, len(libcodes)):
		cnvvalues = []
		positions = []

		for cnvobject in CNV.objects.filter(library__library_code=libcodes[x]).filter(cnv_type__cvterm='CNV').filter(chromosome__chromosome_name=chromosome):
			cnvvalues.append(cnvobject.cnv_value)
			positions.append(cnvobject.stop)

		graph.line(x=positions, y=cnvvalues, legend=libcodes[x], line_color=colors[x], line_dash=linestyles[x], line_width=2)
		graph.xaxis[0].formatter = NumeralTickFormatter(format="0")
		graph.circle(x=positions, y=cnvvalues, fill_color=colors[x], size=4, color=colors[x])

		graph.x_range = Range1d(0, positions[-1])

		max_cnv = max(max_cnv, max(cnvvalues))

	graph.y_range = Range1d(0, max_cnv+5)

	script, div = components(graph)
	charts[chromosome] = [script, div]

	return HttpResponse(json.dumps(charts))


def compare_libraries_cnv(request, experimentId):
	"""
	Display CNV chart(s)
	:param request: libcodes, referencegenome/resultids
	:return: all chart objects
	"""

	# kwargs = {'listoflinks': listoflinks, 'title': "Comparing CNVs"}

	if request.method == 'POST':
		# get params from form
		libcodes = request.POST.getlist('libcodes', '')
		colors = []
		linestyles = []
		for libcode in libcodes:
			colors.append(request.POST.get(libcode, ''))
			linestyles.append(request.POST.get('linetype_'+libcode, ''))

		# get chromosome list
		chromosomes =  list(set(CNV.objects.filter(library__library_code__in=libcodes).filter(cnv_type__cvterm='CNV').order_by("chromosome__chromosome_name").values_list("chromosome__chromosome_name", flat=True)))
		chromosomes.sort()


		return render_to_response('snpdb/compare_libraries_cnv.html', {'libcodes': json.dumps(libcodes),
		                                                                'colors': json.dumps(colors),
		                                                                'linestyles': json.dumps(linestyles),
		                                                                'charts': "True",
		                                                                'chromosomes': chromosomes,
		                                                                'exp_id': experimentId}, context_instance=RequestContext(request))


	else:
		exp = Experiment.objects.get(id=experimentId)

		print "Exp: ", exp

		libs = []
		for sample in exp.samples.all():
			for lib in sample.library_set.all():
				libs.append(lib)

	return render_to_response('snpdb/compare_libraries_cnv.html', {'libs': libs,
	                                                                'exp': exp,
	                                                                'exp_id': experimentId,
	                                                                'colors': ['blue', 'orange', 'red', 'green', 'yellow', 'purple', 'pink', 'black', 'gray', 'cyan', 'white'],
	                                                                'linestyles': ['solid', 'dotted', 'dashed'],
	                                                                'modes': ['Median', 'Mean'],
	                                                                'windowsize': 100,
	                                                                'cnvcutoff': 0.75}, context_instance=RequestContext(request))


def create_cnv_graphs(request):
	data = json.loads(request.body)

	linestyle = data['linestyles']
	colors = data['colors']
	group1_libs = data['group1_libs']
	group2_libs = data['group2_libs']
	summary_mode = data['mode']
	cnvcutoff = data['cnvcutoff']
	chromosome = data['chromosome']
	windowsize = int(data['windowsize'])

	# prepare legands [not displayed yet]
	# // TODO: display common legend on page somewhere. not per plot


	# read in cnv values for each chromosome; for selected set of libraries
	group1_masterdict = create_libwise_cnvdict(request, chromosome, group1_libs)
	group2_masterdict = create_libwise_cnvdict(request, chromosome, group2_libs)
	group1_summarydict = add_group_summary_track_chrom(request, group1_masterdict, summary_mode, group1_libs)
	group2_summarydict = add_group_summary_track_chrom(request, group2_masterdict, summary_mode, group2_libs)

	# Build a master master dict with all indiviudal cnvs and summarized cnvs
	# structure of this will be. full_master{chromosome}{group1|group2}{libcode(s)|summary}=[cnv values]
	full_masterdict = defaultdict(dict)

	#add group 1
	group1dict = defaultdict(str)
	group1dict['summary'] = group1_summarydict[chromosome]
	for libcode, cnvvalues in group1_masterdict[chromosome].items():
		group1dict[libcode] = cnvvalues
	full_masterdict[chromosome]['group1'] = group1dict

	#add group 2
	group2dict = defaultdict(str)
	group2dict['summary'] = group2_summarydict[chromosome]
	for libcode, cnvvalues in group2_masterdict[chromosome].items():
		group2dict[libcode] = cnvvalues
	full_masterdict[chromosome]['group2'] = group2dict

	#find out #sections for each chr
	chrsections = {}
	for libcode, cnvvalues in group1_masterdict[chromosome].items():
		chrsections[chromosome] = int(math.floor(len(cnvvalues) / windowsize))

	charts = find_cnv_diff_create_images_chrom(request, full_masterdict, cnvcutoff, colors, linestyle, group1_libs, group2_libs)

	return HttpResponse(json.dumps(charts))


def compare_libs_cnv(request, experimentId):
	if request.method == 'POST':
		# get params from form
		group1_libcodes = request.POST.getlist('group1_libcodes', '')
		group2_libcodes = request.POST.getlist('group2_libcodes', '')
		group1_color = request.POST.get('group1_color')
		group2_color = request.POST.get('group2_color')
		group1_style = request.POST.get('group1_style')
		group2_style = request.POST.get('group2_style')
		summary_mode = request.POST.get('summary_mode')
		exp = request.POST.get('exp')
		cnvcutoff = request.POST.get('cnvcutoff', '')
		colors = [group1_color.encode('UTF8'), group2_color.encode('UTF8')]
		linestyles = [group1_style, group2_style]
		windowsize = request.POST.get('windowsize', '')
		windowsize = int(windowsize)

		group1_libs = [x.encode("UTF8") for x in group1_libcodes]
		group2_libs = [x.encode("UTF8") for x in group2_libcodes]

		chromosomes = list(set(CNV.objects.filter(library__library_code__in=group1_libcodes).filter(cnv_type__cvterm='CNV').values_list("chromosome__chromosome_name", flat=True)))
		chromosomes.sort()

		return render_to_response('snpdb/test_compare_libs_cnv.html', {'group1_libs': json.dumps(group1_libs),
		                                                                'group2_libs': json.dumps(group2_libs),
		                                                                'colors': json.dumps(colors),
		                                                                'linestyles': json.dumps(linestyles),
		                                                                'mode': summary_mode,
		                                                                'windowsize': windowsize,
		                                                                'cnvcutoff': cnvcutoff,
		                                                                'accordion': "True",
		                                                                'chromosomes': chromosomes,
		                                                                'exp_id': exp}, context_instance=RequestContext(request))


	else:
		exp = Experiment.objects.get(id=experimentId)
		libs = []
		for sample in exp.samples.all():
			for lib in sample.library_set.all():
				libs.append(lib)
	return render_to_response('snpdb/test_compare_libs_cnv.html',  {'libs': libs,
	                                                                'exp': exp,
	                                                                'colors': ['blue', 'orange', 'red', 'green', 'yellow', 'purple', 'pink', 'black', 'gray', 'cyan', 'white'],
	                                                                'linestyles': ['solid', 'dotted', 'dashed'],
	                                                                'modes': ['Median', 'Mean'],
	                                                                'windowsize': 100,
	                                                                'cnvcutoff': 0.75}, context_instance=RequestContext(request))


def create_libwise_cnvdict(request, chromosome, libcodes):
	masterdict = defaultdict(str)
	# for chromosome in chromosomes:
	chrdict = defaultdict(str)
	for libcode in libcodes:
		cnvvalues = []
		for cnvobject in CNV.objects.filter(library__library_code=libcode).filter(cnv_type__cvterm='CNV').filter(chromosome__chromosome_name=chromosome):
			cnvvalues.append(cnvobject.cnv_value)
		chrdict[libcode] = cnvvalues
	masterdict[chromosome] = chrdict
	return masterdict


def add_group_summary_track_chrom(request, masterdict, summary_mode, libcodes):
	new_masterdict = defaultdict(str)

	chromosome = masterdict.keys()[0]
	chrlen = len(masterdict[chromosome][libcodes[0]])

	# loop through chr and create chr level group summary
	chrwise_summary = []
	for pos in range(0, chrlen - 1):
		svnvalues = []
		for libcode in libcodes:
			svnvalues.append(masterdict[chromosome][libcode][pos])
		if summary_mode == 'Mean':
			chrwise_summary.append(numpy.mean(svnvalues))
		if summary_mode == 'Median':
			chrwise_summary.append(numpy.median(svnvalues))
	new_masterdict[chromosome]=chrwise_summary
	return new_masterdict


def find_cnv_diff_create_images_chrom(request, full_masterdict, cnvcutoff, colors, linestyle, group1_libcodes, group2_libcodes):
	charts = defaultdict(str)
	chromosome = full_masterdict.keys()[0]

	group1_summary_cnvs = full_masterdict[chromosome]['group1']['summary']
	group2_summary_cnvs = full_masterdict[chromosome]['group2']['summary']

	index = 0
	end_pos = len(group1_summary_cnvs)-1

	alllib_cnvvalues = []
	cur_pos = []
	while index < end_pos:
		cnv_diff = group1_summary_cnvs[index] - group2_summary_cnvs[index]

		if abs(cnv_diff) > float(cnvcutoff):
			cur_pos.append(index)
			index += 1

		elif len(cur_pos) > 0:

			flank_dif = False
			for x in range(index, index + 3):
				temp_cnv_dif = group1_summary_cnvs[x] - group2_summary_cnvs[x]

				if abs(temp_cnv_dif) > float(cnvcutoff):
					flank_dif=True

			if flank_dif:
				print "extending: ", cur_pos
				cur_pos.extend(range(index, index+4))
				print cur_pos
				index += 3

			else:
				print "No difference: ", cur_pos
				slice_start = cur_pos[0]
				if slice_start < 0:
					slice_start = 0
				slice_end = index
				if slice_end > end_pos:
					slice_end = end_pos


				alllib_cnvvalues.append(group1_summary_cnvs[slice_start:slice_end])
				alllib_cnvvalues.append(group2_summary_cnvs[slice_start:slice_end])

				labels = []
				for label in range(slice_start, slice_end, 2):
					labels.append(label * 1000)
				labels.append(slice_end * 1000)


				labels = []
				for label in range(slice_start, slice_end, 2):
					labels.append(label * 1000)
				labels.append(slice_end * 1000)

				try:
					gene = Feature.objects.values('geneid', 'fmin', 'fmax').filter(Q(featuretype='gene'), Q(chromosome=chromosome), Q(fmin__range=(labels[0], labels[-1])) | Q(fmax__range=(labels[0], labels[-1])))
				except ObjectDoesNotExist:
					print "There is no gene in this region"

				title = chromosome + ": " + str(labels[0]) + " - " + str(labels[-1])

				group1_y = group1_summary_cnvs[slice_start:slice_end]
				group2_y = group2_summary_cnvs[slice_start:slice_end]

				graph = figure(x_axis_label='Position (bp)', y_axis_label='CNV Values', title=title,
			                plot_height=400, plot_width=800, toolbar_location=None, tools='hover')

				hover = graph.select(dict(type=HoverTool))
				hover.tooltips = [("Position", "@x"), ("CNV Value", "@y")]


				graph.line(x=labels, y=group1_y, line_color=colors[0], line_dash=linestyle[0], line_width=3, legend=', '.join(group1_libcodes))
				graph.xaxis[0].formatter = NumeralTickFormatter(format="0")
				graph.circle(x=labels, y=group1_y, fill_color=colors[0], size=6, color=colors[0])


				min_x = labels[0]
				max_x = labels[-1]
				min_y = -5

				if gene:
					for i in range(0, len(gene)):
						left = min(gene[i]['fmin'], labels[0])
						right = max(gene[i]['fmax'], labels[-1])

						min_x = min(left-500, min_x)
						max_x = max(right+500, max_x)
						min_y = min(min_y, 1.5-i)

						x_pos = numpy.mean([left, right])
						graph.quad(top=[-1 - i], bottom=[-2 - i], left=[left], right=[right], fill_color="#87CEEB", line_color="black")
						glyph = Text(x=x_pos, y=-1.5 - i, text=[gene[i]['geneid']], text_baseline='middle', text_align='center', text_color='black', text_font_size="9pt", text_font_style="bold")
						graph.add_glyph(glyph)


				graph.line(x=labels, y=group2_y, line_color=colors[1], line_dash=linestyle[1], line_width=3, legend=', '.join(group2_libcodes))
				graph.xaxis[0].formatter = NumeralTickFormatter(format="0")
				graph.circle(x=labels, y=group2_y, fill_color=colors[1], size=6, color=colors[1])

				graph.x_range = Range1d(min_x, max_x)
				graph.y_range = Range1d(min_y, max(max(group1_y), max(group2_y))+10)

				script, div = components(graph)
				charts[index] = [script, div]

				index += 3
				cur_pos = []
		else:
			index += 1

	charts = remove_empty_keys(charts)
	charts = OrderedDict(sorted(charts.items()))

	return charts


def remove_empty_keys(d):
    for k in d.keys():
        if not d[k]:
            del d[k]
    return d


