#!/bin/bash

__author__ = 'mcobb'
from GChartWrapper import *
import os
import psycopg2
import csv

dbh = psycopg2.connect(host='ngsdb', database='ngsdb03aa', user='ngsdb03', password='ngsdb03')
cur = dbh.cursor()

path = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir)
chart_path = os.path.join(path, 'snpdb/gcharts/%s_impact.csv')
image_path = os.path.join(path, 'snpdb/static/snps_by_%s.png')
# Google Chart Images
lib_labels = []
lib_legend = []
org_labels = []
org_legend = []
impact_labels = []
high_labels = []
low_labels = []
moderate_labels = []
modifier_labels = []
high_keys = []
low_keys = []
moderate_keys = []
modifier_keys = []
impact_keys = []
high_values = []
low_values = []
moderate_values = []
modifier_values = []
impact_values = []


# Dumps a queryset into a csv file.
def dump(qs, outfile_path):
	writer = csv.writer(open(outfile_path, 'w'))
	keys = []
	values = []
	for obj in qs:
		val = obj[0]
		key = obj[1]
		values.append(int(val))
		if key not in keys:
			keys.append(key)
	value = dict(zip(keys, values))
	# value = [tuple(values[i:i+2]) for i in range(0, len(values), 2)]
	writer.writerow(value.items())
	# for k, v in value.iteritems():
		# writer.writerow(k, v)


def main():
	cur.execute('SELECT count(snp_id), effect_string FROM snpdb_effect WHERE effect_id=1 GROUP BY effect_string')
	impact = cur.fetchall()
	# impact = Effect.objects.filter(effect_id=1).values("effect_string").annotate(Count('snp'))
	dump(impact, chart_path % 'impact')
	for obj in impact:
		val = obj[0]
		key = obj[1]
		impact_values.append(int(val))
		if val not in impact_keys:
			impact_keys.append(key)
	impact_snp_total = int(sum(impact_values))
	for x in impact_values:
		percentage = float(x)/float(impact_snp_total)*100
		impact_labels.append(round(percentage,2))
	snps_by_impact = Pie(impact_labels).label(*impact_labels).legend(*impact_keys).color("919dab", "D2E3F7",
	                                                                                     "658CB9", "88BBF7",
	                                                                                     "666E78").size(450, 200)

	snps_by_impact.image().save(image_path % 'impact', 'png')
	print "impact files saved"

	cur.execute('SELECT count(snp_id), effect_class FROM snpdb_effect WHERE effect_id=1 and effect_string=%s GROUP BY effect_class', ('LOW',))
	low = cur.fetchall()
	# low = Effect.objects.filter(effect_id=1, effect_string="LOW").values("effect_class").annotate(Count('snp'))
	dump(low, chart_path % 'low')
	for obj in low:
		val = obj[0]
		key = obj[1]
		low_values.append(int(val))
		if val not in low_keys:
			low_keys.append(key)
	low_snp_total = sum(low_values)
	for x in low_values:
		percentage = float(x)/float(low_snp_total)*100
		low_labels.append(round(percentage, 2))
	snps_by_low = Pie(low_labels).label(*low_labels).legend(*low_keys).color("919dab", "D2E3F7",
	                                                                         "658CB9", "88BBF7",
	                                                                         "666E78").size(450, 200)
	snps_by_low.image().save(image_path % 'low', 'png')
	print "low files saved"

	cur.execute('SELECT count(snp_id), effect_class FROM snpdb_effect WHERE effect_id=1 and effect_string=%s GROUP BY effect_class', ('HIGH',))
	high = cur.fetchall()
	# high = Effect.objects.filter(effect_id=1, effect_string="HIGH").values("effect_class").annotate(Count('snp'))
	dump(high, chart_path % 'high')
	for obj in high:
		val = obj[0]
		key = obj[1]
		high_values.append(int(val))
		if key not in high_keys:
			high_keys.append(key)
	high_snp_total = int(sum(high_values))
	for x in high_values:
		percentage = float(x)/float(high_snp_total)*100
		high_labels.append(round(percentage, 2))
	snps_by_high_impact = Pie(high_labels).label(*high_labels).legend(*high_keys).color("919dab", "D2E3F7",
	                                                                                    "658CB9", "88BBF7",
	                                                                                    "666E78").size(450, 200)
	snps_by_high_impact.image().save(image_path % 'high', 'png')
	print "high files saved"

	cur.execute('SELECT count(snp_id), effect_class FROM snpdb_effect WHERE effect_id=1 and effect_string=%s GROUP BY effect_class', ('MODERATE',))
	moderate = cur.fetchall()
	# moderate = Effect.objects.filter(effect_id=1, effect_string="MODERATE").values("effect_class").annotate(Count('snp'))
	dump(moderate, chart_path % 'moderate')
	for obj in moderate:
		val = obj[0]
		key = obj[1]
		moderate_values.append(int(val))
		if key not in moderate_keys:
			moderate_keys.append(key)
	moderate_snp_total = int(sum(moderate_values))
	for x in moderate_values:
		percentage = float(x)/float(moderate_snp_total)*100
		moderate_labels.append(round(percentage, 2))
	snps_by_moderate = Pie(moderate_labels).label(*moderate_labels).legend(*moderate_keys).color("919dab", "D2E3F7",
	                                                                                             "658CB9", "88BBF7",
	                                                                                             "666E78").size(550, 200)
	snps_by_moderate.image().save(image_path % 'moderate', 'png')
	print "moderate files saved"


	cur.execute('SELECT count(snp_id), effect_class FROM snpdb_effect WHERE effect_id=1 and effect_string=%s GROUP BY effect_class', ('MODIFIER',))
	modifier = cur.fetchall()
	# modifier = Effect.objects.filter(effect_id=1, effect_string="MODIFIER").values("effect_class").annotate(Count('snp'))
	dump(modifier, chart_path % 'modifier')
	for obj in modifier:
		val = obj[0]
		key = obj[1]
		modifier_values.append(int(val))
		if val not in modifier_keys:
			modifier_keys.append(key)
	modifier_snp_total = int(sum(modifier_values))
	for x in modifier_values:
		percentage = float(x)/float(modifier_snp_total)*100
		modifier_labels.append(round(percentage, 2))
	snps_by_modifier = Pie(modifier_labels).label(*modifier_labels).legend(*modifier_keys).color("919dab", "D2E3F7",
	                                                                                             "658CB9", "88BBF7",
	                                                                                             "666E78").size(450, 200)
	snps_by_modifier.image().save(image_path % 'modifier', 'png')
	print "modifier files saved"


	cur.execute('SELECT count(snp_id), samples_library.library_code FROM snpdb_snp, samples_library WHERE snpdb_snp.library_id=samples_library.id GROUP BY samples_library.library_code')
	lib_count = cur.fetchall()
	# lib_count = SNP.objects.values("library__library_code").distinct().annotate(Count('snp_id'))
	lib_snps = []
	lib_snp_total = 0
	for obj in lib_count:
		val = obj[0]
		key = obj[1]
		lib_snps.append(int(val))
		lib_snp_total += int(val)
		lib_legend.append(key)
	for x in lib_snps:
		percentage = float(x)/float(lib_snp_total)*100
		lib_labels.append(round(percentage, 2))
	snps_by_library = Pie([lib_labels]).label(*lib_labels).legend(*lib_legend).color("919dab", "D2E3F7",
	                                                                                 "658CB9", "88BBF7",
	                                                                                 "666E78").size(450, 200)
	snps_by_library.image()
	snps_by_library.image().save(image_path % 'library', 'png')
	print "saved snps_by_library"



	cur.execute('SELECT count(snp_id), ngsdbview_organism.organismcode FROM snpdb_snp, ngsdbview_organism, ngsdbview_result, ngsdbview_genome WHERE snpdb_snp.result_id = ngsdbview_result.result_id AND ngsdbview_result.genome_id = ngsdbview_genome.genome_id AND ngsdbview_genome.organism_id = ngsdbview_organism.organism_id GROUP BY ngsdbview_organism.organismcode')
	org_count = cur.fetchall()
	# org_count = SNP.objects.values("library__organism__organismcode").distinct().annotate(Count('snp_id'))
	org_snps = []
	org_snp_total = 0
	for obj in org_count:
		val = obj[0]
		key = obj[1]
		org_snp_total += int(val)
		org_snps.append(int(val))
		org_legend.append(key)
	for x in org_snps:
		percentage = float(x)/float(org_snp_total)*100
		org_labels.append(round(percentage, 2))
	snps_by_organism = Pie(org_labels).label(*org_labels).legend(*org_legend).color("919dab", "D2E3F7",
	                                                                                "658CB9", "88BBF7",
	                                                                                "666E78").size(450, 200)
	snps_by_organism.image().save(image_path % 'organism', 'png')
	print "saved snps_by_organism"

main()
