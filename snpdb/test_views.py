__author__ = 'mcobb'
from snpdb.models import *
from samples.models import *
from math import ceil
from ngsdbview.viewtools import *
from GChartWrapper import *
from collections import defaultdict
import numpy as np

from django.conf import settings
# from pygal.style import *


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

		#Adds spacing between chromosomes
		# color_list.append('#F1EEE7')
		# color_list.append('#F1EEE7')

		somyobjects = CNV.objects.filter(library__library_code__in=libcodes).filter(cnv_type__cvterm='Somy')
		contignames = []
		for contig in sorted(list(set(somyobjects.values_list('chromosome__chromosome_name', flat=True)))):
			contignames.append(re.sub(r'\D+', '', re.sub(r'_.+', '', contig)))

		# custom_style = Style(
		# 	background='transparent',
		#     plot_background='#F1EEE7',
		#     transition='200ms ease-in',
		# 	colors=(color_list),
		#     foreground_dark='black',
		#     foreground='black',
		#     foreground_light='black',
		#     opacity='.6',
		# )


		somy_dict = {}
		# chart = pygal.Bar(style=custom_style, width=1000, height=500)

		max_somy = 0
		for libcode in libcodes:
			somy_for_lib = []
			for somyvalue in somyobjects.filter(library__library_code=libcode).order_by('chromosome__chromosome_name').values_list('cnv_value', flat=True):
				somy_for_lib.append(somyvalue)

				if somyvalue > max_somy:
					max_somy = somyvalue

			somy_dict[libcode] = somyvalue




		#Adds spacing between chromosomes
		chart.add('', [None])
		chart.add('', [None])

		chart.x_labels = contignames
		chart.value_formatter = lambda x: "%.3f" % x


		return render_to_response('snpdb/compare_libraries_somy_test.html', {'chart':chart}, context_instance=RequestContext(request))

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

	return render_to_response('snpdb/compare_libraries_somy_test.html', kwargs, context_instance=RequestContext(request))



# def compare_libraries_somy(request, experimentId):
# 	"""
# 	Display somy chart(s)
# 	:param request: libcodes, referencegenome/resultids
# 	:return: all chart objects
# 	"""
#
# 	kwargs = {}
# 	#kwargs['user']=user
# 	kwargs['listoflinks']=listoflinks
# 	kwargs['title']="Comparing Somy"
#
# 	if request.method == 'POST':
#
# 		libcodes = request.POST.getlist('libcodes', '')
#
# 		color_list = []
# 		legendvalues = []
# 		for libcode in libcodes:
# 			libobj = Library.objects.get(library_code=libcode)
# 			legendvalues.append(libobj.library_code+'('+libobj.sampleid.samplename+')')
# 			color = request.POST.get(libcode)
# 			color_list.append(color)
#
# 		#Adds spacing between chromosomes
# 		color_list.append('#F1EEE7')
# 		color_list.append('#F1EEE7')
#
# 		custom_style = Style(
# 			background='transparent',
# 		    plot_background='#F1EEE7',
# 		    transition='200ms ease-in',
# 			colors=(color_list),
# 		    foreground_dark='black',
# 		    foreground='black',
# 		    foreground_light='black',
# 		    opacity='.6',
# 		)
#
# 		somyobjects = CNV.objects.filter(library__library_code__in=libcodes).filter(cnv_type__cvterm='Somy')
# 		contignames = []
# 		for contig in sorted(list(set(somyobjects.values_list('chromosome__chromosome_name', flat=True)))):
# 			contignames.append(re.sub(r'\D+', '', re.sub(r'_.+', '', contig)))
#
# 		# list_of_somy = []
# 		chart = pygal.Bar(style=custom_style, width=1000, height=500)
# 		for libcode in libcodes:
# 			somy_for_lib = []
# 			for somyvalue in somyobjects.filter(library__library_code=libcode).order_by('chromosome__chromosome_name').values_list('cnv_value', flat=True):
# 				somy_for_lib.append(somyvalue)
#
# 			chart.add(libcode, somy_for_lib)
#
# 		#Adds spacing between chromosomes
# 		chart.add('', [None])
# 		chart.add('', [None])
#
# 		chart.x_labels = contignames
# 		chart.value_formatter = lambda x: "%.3f" % x
#
#
# 		return render_to_response('snpdb/compare_libraries_somy_test.html', {'chart':chart}, context_instance=RequestContext(request))
#
# 	else:
# 		exp = Experiment.objects.get(id=experimentId)
# 		kwargs['exp'] = exp
# 		libs = []
# 		for sample in exp.samples.all():
# 			for lib in sample.library_set.all():
# 				libs.append(lib)
#
# 		kwargs['libs'] = libs
# 		kwargs['display_form'] = 'yes'
# 		kwargs['colors'] = ['blue', 'orange', 'red', 'green', 'yellow', 'purple', 'pink', 'black', 'gray', 'cyan', 'white']
#
# 	return render_to_response('snpdb/compare_libraries_somy_test.html', kwargs, context_instance=RequestContext(request))



def compare_libraries_cnv(request, experimentId):
	"""
	Display CNV chart(s)
	:param request: libcodes, referencegenome/resultids
	:return: all chart objects
	"""

	kwargs = {'listoflinks': listoflinks, 'title': "Comparing CNVs"}
	#kwargs['user']=user

	if request.method == 'POST':
		# get params from form
		libcodes = request.POST.getlist('libcodes', '')
		colors = []
		linestyles = []
		for libcode in libcodes:
			colors.append(request.POST.get(libcode, ''))
			linestyles.append(request.POST.get('linetype_'+libcode, ''))

		# prepare legands [not displayed yet]
		# // TODO: display common legend on page somewhere. not per plot
		legendvalues = []
		for libcode in libcodes:
			libobj = Library.objects.get(library_code=libcode)
			legendvalues.append(libobj.library_code+'('+libobj.sampleid.samplename+')')

		# get chromosome list
		chromosomes =  list(set(CNV.objects.filter(library__library_code__in=libcodes).filter(cnv_type__cvterm='CNV').order_by("chromosome__chromosome_name").values_list("chromosome__chromosome_name", flat=True)))
		# chromosomes.sort()

		# read in cnv values for each chromosome; for selected set of libraries
		masterdict = defaultdict(str)
		for chromosome in chromosomes:
			chrdict = defaultdict(str)
			for libcode in libcodes:
				cnvvalues = []
				for cnvobject in CNV.objects.filter(library__library_code=libcode).filter(cnv_type__cvterm='CNV').filter(chromosome__chromosome_name=chromosome):
					cnvvalues.append(cnvobject.cnv_value)
				chrdict[libcode] = cnvvalues
			masterdict[chromosome] = chrdict

		#prepare charts
		charts = defaultdict(str)

		#set window size for each picture
		windowsize = request.POST.get('windowsize', '')
		windowsize = int(windowsize)

		#find out #sections for each chr
		chrsections = {}
		for chromosome in chromosomes:
			for libcode, cnvvalues in masterdict[chromosome].items():
				chrsections[chromosome] = int(math.floor(len(cnvvalues) / windowsize))

		for chromosome in chromosomes:
			chrchartlets = {}

			max_cnv_value = 4
			for libcode, cnv_values in masterdict[chromosome].items():
				if max(cnv_values) > max_cnv_value:
					max_cnv_value = max(cnv_values)


			cnv_linechart = pygal.Line()
			for section in range(1, chrsections[chromosome] + 1):
				slice_start = (section - 1) * windowsize + 1
				slice_end = section * windowsize


				for lib in libcodes:
					cnvvalues = masterdict[chromosome][lib]
					cnv_linechart.add(lib, cnvvalues[slice_start:slice_end])

				labels = []
				for label in range(slice_start, slice_end, 5):
					labels.append(label)
				labels.append(slice_end)

				cnv_linechart.x_labels = labels




				# cnv_linechart = Line(
				# 	alllib_cnvvalues, encoding="text"
				# )
				# cnv_linechart.color(*colors)
				# cnv_linechart.scale(0, int(ceil(max_cnv_value+2))).axes('xyx')
				# cnv_linechart.axes.label(0, *labels)
				# cnv_linechart.grid(1, 25)
				# cnv_linechart.axes.label(1, *range(0, int(ceil(max_cnv_value+2)), int(ceil(max_cnv_value/4))))
				# cnv_linechart.axes.label(2, None, 'Base pair in 1000s', None)
				# #set line style
				# for linestyle in linestyles:
				# 	if linestyle == 'solid':
				# 		cnv_linechart.line(2, 4, 0)
				# 	elif linestyle == 'dotted':
				# 		cnv_linechart.line(2, 1, 1)
				# 	elif linestyle == 'dashed':
				# 		cnv_linechart.line(2, 4, 4)

				# cnv_linechart.size(1000, 200)
				chrchartlets[section] = cnv_linechart

			# dont forget the leftover data
			section = chrsections[chromosome] + 1
			slice_start = (section - 1 ) * windowsize + 1
			slice_end = -1
			alllib_cnvvalues = []
			for lib in libcodes:
				cnvvalues = masterdict[chromosome][lib]
				alllib_cnvvalues.append(cnvvalues[slice_start:slice_end])

			labels = []
			for label in range(slice_start, slice_start+len(alllib_cnvvalues[0]), 5):
				labels.append(label)

			cnv_linechart = Line(
				alllib_cnvvalues, encoding="text"
			)
			cnv_linechart.color(*colors)
			cnv_linechart.scale(0, max_cnv_value+2).axes('xyx')
			cnv_linechart.axes.label(0, *labels)
			# cnv_linechart.grid(1, 25)
			cnv_linechart.axes.label(1, *range(0, int(ceil(max_cnv_value+2)), int(ceil(max_cnv_value/4))))
			cnv_linechart.axes.label(2, None, 'Base pair in 1000s', None)
			#set line style
			for linestyle in linestyles:
				if linestyle == 'solid':
					cnv_linechart.line(2, 4, 0)
				elif linestyle == 'dotted':
					cnv_linechart.line(2, 1, 1)
				elif linestyle == 'dashed':
					cnv_linechart.line(2, 4, 4)


			chart_length = (1000 / windowsize) * len(alllib_cnvvalues[0])
			cnv_linechart.size(chart_length, 200)
			chrchartlets[section] = cnv_linechart

			charts[chromosome] = chrchartlets

		kwargs['charts'] = charts
		kwargs['display_chart']='yes'

	else:
		exp = Experiment.objects.get(id=experimentId)
		kwargs['exp'] = exp
		libs = []
		for sample in exp.samples.all():
			for lib in sample.library_set.all():
				libs.append(lib)
		print libs
		kwargs['libs'] = libs
		kwargs['display_form'] = 'yes'
		kwargs['colors'] = ['blue', 'orange', 'red', 'green', 'yellow', 'purple', 'pink', 'black', 'gray', 'cyan', 'white']
		kwargs['linestyles'] = ['solid', 'dotted', 'dashed']
		kwargs['windowsize'] = 100
		kwargs['mincutoff'] = 0.75

	return render_to_response('snpdb/compare_libraries_cnv_test.html', kwargs, context_instance=RequestContext(request))

