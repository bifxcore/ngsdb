__author__ = 'mcobb'
from snpdb.models import *
from samples.models import *
from ngsdbview.viewtools import *
from collections import defaultdict, OrderedDict
import numpy
import json
from bokeh.charts import Bar
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.models import NumeralTickFormatter, HoverTool, BoxZoomTool, ResetTool, PanTool, PreviewSaveTool
from bokeh.io import hplot, output_file, show

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

		return render_to_response('snpdb/compare_libraries_somy_test.html', {"script":script, "div":div}, context_instance=RequestContext(request))

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

		# get chromosome list
		chromosomes =  list(set(CNV.objects.filter(library__library_code__in=libcodes).filter(cnv_type__cvterm='CNV').order_by("chromosome__chromosome_name").values_list("chromosome__chromosome_name", flat=True)))

		graphs = {}

		# read in cnv values for each chromosome; for selected set of libraries
		for chromosome in chromosomes:
			graph = figure(x_axis_label='Position (bp)', y_axis_label='CNV Values',
			               tools=[BoxZoomTool(), PanTool(), HoverTool(tooltips = [("position", "@x"), ("CNV Value", "@y")]),
			                      ResetTool(), PreviewSaveTool()], plot_height=800, plot_width=1300, toolbar_location="left")
			for x in range(0, len(libcodes)):
				cnvvalues = []
				positions = []

				for cnvobject in CNV.objects.filter(library__library_code=libcodes[x]).filter(cnv_type__cvterm='CNV').filter(chromosome__chromosome_name=chromosome):
					cnvvalues.append(cnvobject.cnv_value)
					positions.append(cnvobject.stop)

				graph.line(x=positions, y=cnvvalues, legend=libcodes[x], line_color=colors[x], line_dash=linestyles[x], line_width=2)
				graph.xaxis[0].formatter = NumeralTickFormatter(format="0")
				graph.circle(x=positions, y=cnvvalues, fill_color=colors[x], size=4, color=colors[x])

			script, div = components(graph)
			graphs[chromosome] = [script, div]

		graph = OrderedDict(sorted(graphs.items()))

		kwargs['charts'] = graph
		kwargs['display_chart']='yes'

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
		kwargs['linestyles'] = ['solid', 'dotted', 'dashed']
		kwargs['windowsize'] = 100
		kwargs['mincutoff'] = 0.75

	return render_to_response('snpdb/compare_libraries_cnv_test.html', kwargs, context_instance=RequestContext(request))


def create_cnv_graphs(request):
	json = request.POST.get('json_dump')

	print json

	group1_libs = request.POST.getlist('group1_libs', '')[0]
	group2_libs = request.POST.getlist('group2_libs', '')[0]
	colors = request.POST.getlist('colors', '')[0]
	styles = request.POST.getlist('linestyles', '')[0]

	# group1_libcodes = libcodes[0]
	# group2_libcodes = libcodes[1]
	# group1_color = colors[0]
	# group2_color = colors[1]
	#
	# group1_style = styles[0]
	# group2_style = styles[1]

	summary_mode = request.POST.get('summary_mode')
	cnvcutoff = request.POST.get('cnvcutoff', '')

	chromosome = request.POST.get('chromosome')

	print type(group1_libs.encode('utf8'))

	print chromosome, group1_libs.encode('utf8'), group2_libs, colors, styles, summary_mode, cnvcutoff

	# for libcode in group1_libcodes:
	# 	colors.append(request.POST.get(libcode, ''))
	# 	styles.append(request.POST.get('linetype_'+libcode, ''))

	# prepare legands [not displayed yet]
	# // TODO: display common legend on page somewhere. not per plot

	# get chromosome list
	chromosomes = list(set(CNV.objects.filter(library__library_code__in=group1_libcodes).filter(cnv_type__cvterm='CNV').values_list("chromosome__chromosome_name", flat=True)))
	chromosomes.sort()

	# read in cnv values for each chromosome; for selected set of libraries
	group1_masterdict = create_chrwise_libwise_cnvdict(request, chromosomes, group1_libcodes)
	group2_masterdict = create_chrwise_libwise_cnvdict(request, chromosomes, group2_libcodes)
	group1_summarydict = add_group_summary_track(request, group1_masterdict, summary_mode)
	group2_summarydict = add_group_summary_track(request, group2_masterdict, summary_mode)

	# Build a master master dict with all indiviudal cnvs and summarized cnvs
	# structure of this will be. full_master{chromosome}{group1|group2}{libcode(s)|summary}=[cnv values]
	full_masterdict = defaultdict(dict)
	for chromosome in chromosomes:
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

	#prepare charts
	charts = defaultdict(str)

	#set window size for each picture
	windowsize = request.POST.get('windowsize', '')
	windowsize = int(windowsize)
	#find out #sections for each chr
	chrsections = {}
	for chromosome in chromosomes:
		for libcode, cnvvalues in group1_masterdict[chromosome].items():
			chrsections[chromosome] = int(math.floor(len(cnvvalues) / windowsize))

	charts = find_cnv_diff_create_images(request, full_masterdict, cnvcutoff, colors, styles, group1_libcodes, group2_libcodes)

	kwargs['charts'] = charts
	kwargs['display_chart']='yes'


def test_compare_libs_cnv(request, experimentId):
	kwargs = {'listoflinks': listoflinks, 'title': "Comparing CNVs"}
	#kwargs['user']=user


	if request.method == 'POST':
		# get params from form
		group1_libcodes = request.POST.getlist('group1_libcodes', '')
		group2_libcodes = request.POST.getlist('group2_libcodes', '')
		group1_color = request.POST.get('group1_color', '')
		group2_color = request.POST.get('group2_color', '')
		group1_style = request.POST.get('group1_style', '')
		group2_style = request.POST.get('group2_style', '')
		summary_mode = request.POST.get('summary_mode')
		exp = request.POST.get('exp')
		cnvcutoff = request.POST.get('cnvcutoff', '')
		colors = [group1_color, group2_color]
		linestyles = [group1_style, group2_style]
		windowsize = request.POST.get('windowsize', '')
		windowsize = int(windowsize)

		group1_libs = [x.encode("UTF8") for x in group1_libcodes]
		group2_libs = [x.encode("UTF8") for x in group2_libcodes]

		chromosomes = list(set(CNV.objects.filter(library__library_code__in=group1_libcodes).filter(cnv_type__cvterm='CNV').values_list("chromosome__chromosome_name", flat=True)))
		chromosomes.sort()

		kwargs['group1_libs'] = group1_libs
		kwargs['group2_libs'] = group2_libs
		kwargs['colors'] = colors
		kwargs['linestyles'] = linestyles
		kwargs['mode'] = summary_mode
		kwargs['windowsize'] = windowsize
		kwargs['cnvcutoff'] =  cnvcutoff
		kwargs['accordion'] = "True"
		kwargs['chromosomes'] = chromosomes
		kwargs['exp_id'] = exp

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
		kwargs['linestyles'] = ['solid', 'dotted', 'dashed']
		kwargs['modes'] = ['Median', 'Mean']
		kwargs['windowsize'] = 100
		kwargs['cnvcutoff'] =  0.75

	return render_to_response('snpdb/test_compare_libs_cnv.html', kwargs, context_instance=RequestContext(request))


def compare_libraries_cnv_filter(request, experimentId):
	"""
	Display CNV chart(s)
	:param request: libcodes, referencegenome/resultids
	:return: all chart objects
	"""

	kwargs = {'listoflinks': listoflinks, 'title': "Comparing CNVs"}
	#kwargs['user']=user

	if request.method == 'POST':
		# get params from form
		group1_libcodes = request.POST.getlist('group1_libcodes', '')
		group2_libcodes = request.POST.getlist('group2_libcodes', '')
		group1_color = request.POST.get('group1_color', '')
		group2_color = request.POST.get('group2_color', '')
		group1_style = request.POST.get('group1_style', '')
		group2_style = request.POST.get('group2_style', '')
		summary_mode = request.POST.get('summary_mode')
		cnvcutoff = request.POST.get('cnvcutoff', '')
		colors = [group1_color, group2_color]
		linestyles = [group1_style, group2_style]

		for libcode in group1_libcodes:
			colors.append(request.POST.get(libcode, ''))
			linestyles.append(request.POST.get('linetype_'+libcode, ''))

		# prepare legands [not displayed yet]
		# // TODO: display common legend on page somewhere. not per plot

		# get chromosome list
		chromosomes = list(set(CNV.objects.filter(library__library_code__in=group1_libcodes).filter(cnv_type__cvterm='CNV').values_list("chromosome__chromosome_name", flat=True)))
		chromosomes.sort()

		# read in cnv values for each chromosome; for selected set of libraries
		group1_masterdict = create_chrwise_libwise_cnvdict(request, chromosomes, group1_libcodes)
		group2_masterdict = create_chrwise_libwise_cnvdict(request, chromosomes, group2_libcodes)
		group1_summarydict = add_group_summary_track(request, group1_masterdict, summary_mode)
		group2_summarydict = add_group_summary_track(request, group2_masterdict, summary_mode)

		# Build a master master dict with all indiviudal cnvs and summarized cnvs
		# structure of this will be. full_master{chromosome}{group1|group2}{libcode(s)|summary}=[cnv values]
		full_masterdict = defaultdict(dict)
		for chromosome in chromosomes:
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

		#prepare charts
		charts = defaultdict(str)

		#set window size for each picture
		windowsize = request.POST.get('windowsize', '')
		windowsize = int(windowsize)
		#find out #sections for each chr
		chrsections = {}
		for chromosome in chromosomes:
			for libcode, cnvvalues in group1_masterdict[chromosome].items():
				chrsections[chromosome] = int(math.floor(len(cnvvalues) / windowsize))

		# Create chart for each section of the chromosome if filter cnvvalue is set to Zero
		if cnvcutoff == "0":
			for chromosome in chromosomes:
				chrchartlets = {}

				for section in range(1, chrsections[chromosome]):
					slice_start = (section - 1) * windowsize + 1
					slice_end = section * windowsize
					alllib_cnvvalues = []
					for group, libcodedict in full_masterdict[chromosome].items():
						for libcode, cnvvalues in libcodedict.items():
							if libcode == 'summary':
								alllib_cnvvalues.append(cnvvalues[slice_start:slice_end])
						labels = []
						for label in range(slice_start, slice_end, 5):
							labels.append(label)
						labels.append(slice_end)

					print alllib_cnvvalues

					graph = figure(x_axis_label='Position (bp)', y_axis_label='CNV Values',
			                plot_height=200, plot_width=200, toolbar_location=None)

					graph.line(x=graph_positions, y=labels, legend=", ".join(group1_libcodes), line_color=group1_color, line_dash=group1_style, line_width=2)
					graph.xaxis[0].formatter = NumeralTickFormatter(format="0")
					graph.circle(x=graph_positions, y=labels, fill_color=group1_color, size=4, color=group1_color)

					graph.line(x=graph_positions, y=labels, legend=", ".join(group2_libcodes), line_color=group2_color, line_dash=group2_style, line_width=2)
					graph.xaxis[0].formatter = NumeralTickFormatter(format="0")
					graph.circle(x=graph_positions, y=labels, fill_color=group2_color, size=4, color=group2_color)

					# cnv_linechart = Line( alllib_cnvvalues, encoding="text" )
					# cnv_linechart.color(colors[0], colors[1])
					# cnv_linechart.scale(0, 4).axes('xyx')
					# cnv_linechart.axes.label(0, *labels)
					# cnv_linechart.grid(1, 25)
					# cnv_linechart.axes.label(1, *range(0, 5, 1))
					# cnv_linechart.axes.label(2, None, 'Base pair in 1000s', None)
					#set line style
					# for linestyle in linestyles:
					# 	if linestyle == 'solid':
					# 		cnv_linechart.line(2, 4, 0)
					# 	elif linestyle == 'dotted':
					# 		cnv_linechart.line(2, 1, 1)
					# 	elif linestyle == 'dashed':
					# 		cnv_linechart.line(2, 4, 4)

					# cnv_linechart.size(1000, 200)

					script, div = components(graph)
					chrchartlets[section] = [script, div]


				# # dont forget the leftover data
				section = chrsections[chromosome] + 1
				slice_start = (section - 1 ) * windowsize + 1
				slice_end = -1
				alllib_cnvvalues = []
				for group, libcodedict in full_masterdict[chromosome].items():
					for libcode, cnvvalues in libcodedict.items():
						if libcode == 'summary':
							alllib_cnvvalues.append(cnvvalues[slice_start:slice_end])
					labels = []
					for label in range(slice_start, slice_start+len(alllib_cnvvalues[0]), 5):
						labels.append(label)


					graph = figure(x_axis_label='Position (bp)', y_axis_label='CNV Values',
			                plot_height=200, plot_width=200, toolbar_location=None)

					graph.line(x=graph_positions, y=group1, legend=", ".join(group1_libcodes), line_color=group1_color, line_dash=group1_style, line_width=2)
					graph.xaxis[0].formatter = NumeralTickFormatter(format="0")
					graph.circle(x=graph_positions, y=group1, fill_color=group1_color, size=4, color=group1_color)

					graph.line(x=graph_positions, y=group2, legend=", ".join(group2_libcodes), line_color=group2_color, line_dash=group2_style, line_width=2)
					graph.xaxis[0].formatter = NumeralTickFormatter(format="0")
					graph.circle(x=graph_positions, y=group2, fill_color=group2_color, size=4, color=group2_color)

					script, div = components(graph)
					chrchartlets[section] = [script, div]

					charts[chromosome] = chrchartlets
		else:
			# cnvcut off is not zero
			charts = find_cnv_diff_create_images(request, full_masterdict, cnvcutoff, colors, linestyles, group1_libcodes, group2_libcodes)

		kwargs['charts'] = charts
		kwargs['display_chart']='yes'

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
		kwargs['linestyles'] = ['solid', 'dotted', 'dashed']
		kwargs['modes'] = ['Median', 'Mean']
		kwargs['windowsize'] = 200
		kwargs['cnvcutoff'] =  0.75

	return render_to_response('snpdb/compare_libraries_cnv_filter_test.html', kwargs, context_instance=RequestContext(request))



def create_chrwise_libwise_cnvdict(request, chromosomes, libcodes):
	masterdict = defaultdict(str)
	for chromosome in chromosomes:
		chrdict = defaultdict(str)
		for libcode in libcodes:
			cnvvalues = []
			for cnvobject in CNV.objects.filter(library__library_code=libcode).filter(cnv_type__cvterm='CNV').filter(chromosome__chromosome_name=chromosome):
				cnvvalues.append(cnvobject.cnv_value)
			chrdict[libcode] = cnvvalues
		masterdict[chromosome] = chrdict
	return masterdict


def add_group_summary_track(request, masterdict, summary_mode):
	new_masterdict = defaultdict(str)
	for chromosome, chrleveldict in masterdict.items():
		# find chr length
		libcodes = chrleveldict.keys()
		chrlen = len(chrleveldict[libcodes[0]])
		# loop thru chr and create chr level group summary
		chrwise_summary = []
		for pos in range(0, chrlen - 1):
			svnvalues = []
			for libcode in libcodes:
				svnvalues.append(chrleveldict[libcode][pos])
			if summary_mode == 'Mean':
				chrwise_summary.append(numpy.mean(svnvalues))
			if summary_mode == 'Median':
				chrwise_summary.append(numpy.median(svnvalues))
		new_masterdict[chromosome]=chrwise_summary
	return new_masterdict


def find_cnv_diff_create_images(request, full_masterdict, cnvcutoff, colors, linestyle, group1_libcodes, group2_libcodes):
	charts = defaultdict(str)
	chromosomes = full_masterdict.keys()
	for chromosome in chromosomes:
		chrchartlets = {}
		group1_summary_cnvs = full_masterdict[chromosome]['group1']['summary']
		group2_summary_cnvs = full_masterdict[chromosome]['group2']['summary']
		section = 0
		for pos in range(0, len(group1_summary_cnvs)-1):
			is_diff = 'NO'
			cnv_diff = group1_summary_cnvs[pos] - group2_summary_cnvs[pos]
			if abs(cnv_diff) > float(cnvcutoff):
				is_diff = 'YES'

			alllib_cnvvalues = []
			if is_diff == 'YES':
				section += 1
				slice_start = pos - 2
				if slice_start < 0:
					slice_start = 0
				slice_end = pos + 3
				alllib_cnvvalues.append(group1_summary_cnvs[slice_start:slice_end])
				alllib_cnvvalues.append(group2_summary_cnvs[slice_start:slice_end])

				labels = []
				for label in range(slice_start, slice_end, 2):
					labels.append(label)
				labels.append(slice_end)

				graph = figure(x_axis_label='Position (bp)', y_axis_label='CNV Values',
			                plot_height=200, plot_width=400, toolbar_location=None, tools='')

				graph.line(x=labels, y=group1_summary_cnvs[slice_start:slice_end], line_color=colors[0], line_dash=linestyle[0], line_width=2)
				graph.xaxis[0].formatter = NumeralTickFormatter(format="0")
				graph.circle(x=labels, y=group1_summary_cnvs[slice_start:slice_end], fill_color=colors[0], size=4, color=colors[0])

				graph.line(x=labels, y=group2_summary_cnvs[slice_start:slice_end], line_color=colors[1], line_dash=linestyle[1], line_width=2)
				graph.xaxis[0].formatter = NumeralTickFormatter(format="0")
				graph.circle(x=labels, y=group2_summary_cnvs[slice_start:slice_end], fill_color=colors[1], size=4, color=colors[1])

				script, div = components(graph)
				chrchartlets[section] = [script, div]


		charts[chromosome] = chrchartlets

	charts = remove_empty_keys(charts)
	charts = OrderedDict(sorted(charts.items()))

	return charts


def remove_empty_keys(d):
    for k in d.keys():
        if not d[k]:
            del d[k]
    return d