from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.db.models import Q
import csv

from django import forms
from ngsdbview.models import *
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User

from ngsdbview.viewtools import *
from samples.models import Library as samplelibrary

import math

def Contact(request):
	"""Contact us pabes for personnel and email information"""
	[user, availlibs] = getlibraries(request)
	kwargs={}
	kwargs['title']='Contact Us'
	kwargs['listoflinks']=listoflinks
	kwargs['user']=user
	return render_to_response('ngsdbview/contact.html',kwargs,context_instance=RequestContext(request))

def About(request):
	"""About Us page for information about the group and the sbri bifx services..."""
	[user, availlibs] = getlibraries(request)
	kwargs={}
	kwargs['title']='About Us'
	kwargs['listoflinks']=listoflinks
	kwargs['user']=user
	return render_to_response('ngsdbview/aboutus.html',kwargs,context_instance=RequestContext(request))

def Main(request):
	"""Main page"""

	#get user and a list of library id's the uer has access to
	[user, availlibs] = getlibraries(request)
	kwargs={}
	pages={}
	kwargs['user']=user
	kwargs['pages']=pages
	kwargs['contactinfo']='contactus'

	#constrcut and render two data sets as a line graph
	set1 = [];
	set1.append([-1,2])
	set1.append([15,-3])
	set2 = [];
	set2.append([0,0])
	set2.append([10,0])
	seriesnames = ['sname1','sname2']
	kwargs['linegraph'] = constructLineGraph('chartdiv',[set1,set2],seriesnames,'title','xlabel','ylabel')

	#constrcut and render two some data as a pie chart
	data = [['dragons',10],['unicorns',5],['serpents',15],['lochness',10],['waldo',2]]
	kwargs['piechart'] = constructPieChart('piediv',data,'pietitle')

	#passes in the number of links/2
	kwargs['numlinks']=len(listoflinks)/2 if len(listoflinks)%2==0 else len(listoflinks)/2+1
	kwargs['listoflinks'] = listoflinks
	return render_to_response('ngsdbview/main.html',kwargs,context_instance=RequestContext(request))

def ListAnalysisSteps(request, result_id):
	"""List all the analysis steps carried out for a result set"""

	[user, availlibs] = getlibraries(request)
	allsteps = Analysis.objects.filter(result=result_id).order_by('ordinal')

	analysisprop_set = {}
	for step in allsteps:
		analysisprop_set[step.ordinal]=Analysisprop.objects.filter(analysis=step.analysis_id)

	resultids = []
	resultidlist = Analysis.objects.distinct('result').values_list('result_id');
	for id in resultidlist:
	   resultids.append(id[0])

	libcode = samplelibrary.objects.filter(result__result_id=result_id).values_list('library_code', flat=True)[0]
	print libcode
	kwargs = {
		'title':'Detailed Analysis Steps for Library: '+ libcode +  ' & Result id: ' + str(result_id),
		'currentid':result_id,
		'resultids':resultids,
		'allsteps': allsteps,
		'user': user,
		'analysisprop_set':analysisprop_set,
		'listoflinks':listoflinks,
	}

	return render_to_response('ngsdbview/list_analysis_steps.html', kwargs, context_instance=RequestContext(request))

#===========================================================================#
#======================Forms used for table view pages==========================#
#===========================================================================#
class libform(forms.Form):
	"""
	Class: libform Purpose: form for searching ngsdbview_library used in the ViewLib view
	"""
	authordesignationfield = forms.CharField(max_length=20, label='Author Initials', required=False)
	organismcodefield = forms.CharField(max_length=20, label='Organism Code', required=False)
	libcodefield = forms.CharField(max_length=20, label='Library Code', required=False)

class resultform(forms.Form):
	"""Class: resultsform
	Purpose: form for searching ngsdbview_result table used in the ViewLib view
	"""

	formfields = ['resultidfield','libcodefield','organismcodefield','iscurrentfield','isobsfield']
	resultidfield = forms.CharField(max_length=20, label='Result ID', required=False)
	libcodefield = forms.CharField(max_length=20, label='Library Code', required=False)
	organismcodefield = forms.CharField(max_length=20, label='Organism Code', required=False)
	iscurrentfield = forms.BooleanField(label='Current?', required=False,initial=True)
	isobsfield = forms.BooleanField(label='Obsolete?', required=False, initial=False)

#=========================View with Forms Definitions===============================#

def ViewResult(request):
	"""function name: ViewResult
	Purpose: makes a query-able view for Result table
	"""

	#gets user and a list of libraries they have access to
	[user, availlibs] = getlibraries(request)

	pagetitle = 'NGSDB Results'

	fields =['result_id','library_code','organism','lifestage','phenotype','librarytype','genome','notes','is_current','is_obsolete']
	preffields =[]
	preffnames = []
	objlist = Result.objects.all()

	#filters objlist based on libraries user has permissions to
	queries = [Q(libraries__library_id=alib) for alib in availlibs]
	if len(availlibs)>0:
		query = combineQueries(queries)
		objlist = objlist.filter(query)

	autocomplist = []
	queries = [Q(library_id=alib) for alib in availlibs]
	query = combineQueries(queries)
	autocomplist.append((constructAutocomplete('libcodefield',samplelibrary.objects.filter(query).values_list('library_code',flat=True))))
	#construct queries to filter by
	queries = [Q(libraries__library_id=alib) for alib in availlibs]
	query = combineQueries(queries)
	autocomplist.append((constructAutocomplete('resultidfield',Result.objects.filter(query).values_list('result_id',flat=True))))
	#this filters library then gets to organism objects by foreign key
	queries = [Q(libraries=alib) for alib in availlibs]
	query = combineQueries(queries)
	availgen = Result.objects.filter(query).values_list('genome',flat=True)
	queries = [Q(genome_id=ao) for ao in availgen]
	query = combineQueries(queries)
	availorgs = Genome.objects.filter(query).values_list('organism',flat=True)
	queries = [Q(organism_id=ao) for ao in availorgs]
	query = combineQueries(queries)
	autocomplist.append((constructAutocomplete('organismcodefield',Organism.objects.filter(query).values_list('organismcode',flat=True))))

	#if POST then change data to be displayed
	#WARNING WARNING ONE OF THE T/F FIELDS IS SET TO TRUE ALL THE TIME SO
	# POST IS ALWAYS TRUE!
	if request.method == "POST":

		form = resultform(request.POST)

		#checks form for validity, cleans it and performs filtering
		if form.is_valid():

			searchdisp = 'Searching for ........... '
			origlen = len(searchdisp)

			libcodefield = form.cleaned_data['libcodefield']
			resultidfield = form.cleaned_data['resultidfield']
			organismcodefield = form.cleaned_data['organismcodefield']
			iscurrentfield = form.cleaned_data['iscurrentfield']
			isobsfield = form.cleaned_data['isobsfield']

		#if_inputs = 0 #checks whether any nonbooleanfields have been posted

			if libcodefield:
				#objlist =  objlist.filter(libraryresult__library__librarycode__icontains=libcodefield)
				objlist =  objlist.filter(libraries__library_code__icontains=libcodefield)
				searchdisp = searchdisp + '[' + libcodefield + '] in field [library_code]'
				if_inputs=1
			if resultidfield:
				objlist =  objlist.filter(result_id__icontains=resultidfield)
				if len(searchdisp)>origlen:    searchdisp += ', '
				searchdisp = searchdisp + '[' + resultidfield + '] in field [resultid]'
				if_inputs=1
			if organismcodefield:
				objlist =  objlist.filter(genome__organism__organismcode__icontains=organismcodefield)
				if len(searchdisp)>origlen:
					searchdisp += ', '
				searchdisp = searchdisp + '[' + organismcodefield + '] in field [organismcode]'
				if_inputs=1

			if isobsfield:
				objlist =  objlist.filter(is_obsolete=True)
				if len(searchdisp)>origlen:
					searchdisp += ', '
				searchdisp = searchdisp + '[True] in field [is_obslete]'
				if_inputs=1
			else:
				objlist =  objlist.filter(is_obsolete=False)
				if len(searchdisp)>origlen:
					searchdisp += ', '
				searchdisp = searchdisp + '[False] in field [is_obslete]'
				if_inputs=1

			if iscurrentfield:
				objlist =  objlist.filter(is_current=True) # DEFAUT WAS TRUE THEREFORE A ISCURRENTFIELD INPUT IS FALSE
				if len(searchdisp)>origlen:
					searchdisp += ', '
				if if_inputs==1 or isobsfield:
					searchdisp = searchdisp + '[True] in field [is_current]'
				else: #if no entry and isobsfield not checked
					searchdisp = 'Please enter in keywords to search.'
			else:
				objlist =  objlist.filter(is_current=False) #DEFAULT WAS TRUE SO NO INPUT IS TRUE BY DEFAULT
				if len(searchdisp)>origlen:
					searchdisp += ', '
				searchdisp = searchdisp + '[false] in field [is_current]'

	else:
		#if not search, asks for search and sets starting ind back to 0
		searchdisp = 'Please enter in keywords to search.'
		searchdisp = searchdisp + '[False] in field [is_obslete]'
		form = resultform() #clears the form

	mylist = {}
	#initiate has
	for ff in fields:
		mylist[ff] = []

	for obj in objlist:
		mylist['result_id'].append(obj.result_id)
		mylist['notes'].append(obj.notes)
		mylist['is_current'].append(obj.is_current)
		mylist['is_obsolete'].append(obj.is_obsolete)
		mylist['organism'].append(obj.genome.organism.organismcode)
		mylist['genome'].append(obj.genome.source + " " + obj.genome.version)
		mylist['librarycode'].append(obj.libraries.all()[0].library_code)
		mylist['librarytype'].append(obj.libraries.all()[0].librarytype.type)
		mylist['lifestage'].append(obj.libraries.all()[0].lifestage.lifestage)
		mylist['phenotype'].append(obj.libraries.all()[0].phenotype)


	#orders columns in specified order
	x =0
	newlist = []
	for i in range(len(mylist['result_id'])):
		tup = [mylist[f][i] for f in fields]
		tup.insert(0,x) #for record numbers
		newlist.append(tup)
		x = x+1

	objlist = newlist


	args = {
		'autocomplist':autocomplist,
		'pagetitle':pagetitle,
		'form':form,
		'fields':fields,
		'preffnames':preffnames,
		'objlist':objlist,
		'request':request,
		'searchdisp':searchdisp,
		'user':user,
	}

	#render for display
	#return rendertableview(pagetitle,form,fields,preffnames,objlist,request,page_no,nlimit,searchdisp,user)
	return rendertableview(**args)


def ViewLib(request):
	"""function name: ViewLib
	purpose: creates view for searching based on set search paramters for a given table
	calls: libform, getFieldsFrom, rendertableview
	"""
	#gets user and a list of libraries they have access to
	[user, availlibs] = getlibraries(request)

	pagetitle = 'NGSDB Library List'

	#NEED TO EDIT THESE 2 TOGETHER
	#preffields =['author','downloaddate','collaborator'] # if blank will display all fields, can also set order with this list
	preffields =['author','colloborator','downloaddate','organism','phenotype','notes','flowcell','library_code','librarysize','librarytype']
	preffnames = []
	fields = getFieldsFrom(Library, preffields) #gets fields from the library, if preffields sets returns without doing anything
	objlist = samplelibrary.objects.all()

	autocomplist = []
	#construct queries to filter by
	queries = [Q(library_id=alib) for alib in availlibs]
	query = combineQueries(queries)
	autocomplist.append((constructAutocomplete('libcodefield',samplelibrary.objects.filter(query).values_list('library_code',flat=True))))
	#this filters library then gets to organism objects by foreign key
	queries = [Q(library_id=alib) for alib in availlibs]
	query = combineQueries(queries)
	availorgs = samplelibrary.objects.filter(query).values_list('organism',flat=True)
	queries = [Q(organism_id=ao) for ao in availorgs]
	query = combineQueries(queries)
	autocomplist.append((constructAutocomplete('organismcodefield',Organism.objects.filter(query).values_list('organismcode',flat=True))))
	#this filters for authordesignationfield
	queries = [Q(library_id=alib) for alib in availlibs]
	query = combineQueries(queries)
	availauths = samplelibrary.objects.filter(query).values_list('author',flat=True)
	queries = [Q(author_id=ao) for ao in availauths]
	query = combineQueries(queries)
	autocomplist.append((constructAutocomplete('authordesignationfield',Author.objects.filter(query).values_list('designation',flat=True))))

	#constructing a query to incorporate all libaries-- this is important because
	queries = [Q(library_id=alib) for alib in availlibs]
	if len(availlibs)>0:
		query = queries.pop()
		for item in queries:
			query |= item
		objlist = objlist.filter(query)
	else:
		objlist = []

	#if POST then change data to be displayed
	if request.method == "POST":
		form = libform(request.POST)

		#checks form for validity, cleans it and performs filtering
		if form.is_valid():
			libcodefield = form.cleaned_data['libcodefield']
			organismcodefield = form.cleaned_data['organismcodefield']
			authordesignationfield = form.cleaned_data['authordesignationfield']
			searchdisp = 'Searching for ........... '
			origlen = len(searchdisp)

			if libcodefield:
				objlist =  objlist.filter(library_code__icontains=libcodefield)
				searchdisp = searchdisp + '[' + libcodefield + '] in field [library_code]'
			if organismcodefield:
				objlist =  objlist.filter(organism__organismcode__icontains=organismcodefield)
				if len(searchdisp)>origlen:    searchdisp += ', '
				searchdisp = searchdisp + ' [' + organismcodefield + '] in field [organismcode]'
			if authordesignationfield:
				objlist =  objlist.filter(author__designation__icontains=authordesignationfield)
				if len(searchdisp)>origlen:    searchdisp += ', '
				searchdisp = searchdisp + ' [' + authordesignationfield + '] in field [author]'

		#if blank search asks for user to search
		if not (libcodefield or organismcodefield or authordesignationfield):
			searchdisp = 'Please enter in keywords to search.'

	else:
		#if not search, asks for search and sets starting ind back to 0
		searchdisp = 'Please enter in keywords to search.'
		form = libform() #clears the form

	#builds table
	mylist = []
	#give each row number starting from 0
	x=0
	for obj in objlist:
		tup = [getattr(obj,f, None) for f in fields]
		tup.insert(0,x) #for record count number
		mylist.append(tup)
		x = x+1

	objlist = mylist

	args = {
		'autocomplist':autocomplist,
		'pagetitle':pagetitle,
		'form':form,
		'fields':fields,
		'preffnames':preffnames,
		'objlist':objlist,
		'request':request,
		'searchdisp':searchdisp,
		'user':user,
	}
	#render for display
	#return rendertableview(pagetitle,form,fields,preffnames,objlist,request,page_no,nlimit,searchdisp,user)
	return rendertableview(**args)

