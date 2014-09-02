#this file is to be included in views files

from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.db.models import Q
import csv,math

from django import forms
from ngsdbview.models import *
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User

#============================================================================#
#=========================View Data Structs==============================#
#============================================================================#

listoflinks = [
        ('Dashboard', 'ngsdb/dashboard/'),
        ('AlignmentStats', 'ngsdb/alignstats/'),
        ('List Libraries','ngsdb/listlibraries/'),
        ('List Analyses','ngsdb/ngsdbview_result/'),
        ('Query a Gene','ngsdb/get_results_for_gene/'),
        ('Query multiple Genes', 'ngsdb/query_multigenes/'),
        ('Query Multigene-Multilib', 'ngsdb/query_multigenes_multilibs/'),
        ('Query a Library','ngsdb/get_results_for_library/'),
        ('Get sites for Lib', 'ngsdb/Get_sites_forlib/'),
        ('View Analysis Steps','ngsdb/list_analysis_steps/'),

        ('Get Majorpc', 'ngsdb/get_sitecount_majorpc_forlibs/'),


]


#============================================================================#
#=========================View Helper Functions==============================#
#============================================================================#

def getlibraries(request):
    """function name: getlibraries
    purpose: gets libraries that is permissiable for user to use
    returns: list [user,lib] where user is the logged in user and lib are the libraries user has access to
    """
    if request.user.is_authenticated():
        user=request.user

    #gets user profile corresponding to user
    lib_ids = user.get_profile().libraries.values_list('id',flat=True)

    #changes queryset into a normal list
    liblist =[]
    for li in lib_ids:
        liblist.append(li)

    #gets list of permissions
    return [user, liblist]

def rendertableview(pagetitle,form,fields,preffnames,objlist,request,searchdisp,user,autocomplist):
    """function name: rendertableview
    purpose: gets request and relevant objects and renders the table.html
    arguments:
         pagetitle - tile of page
         form - the form your view queries
         fields - a list of your table attributes being rendered
         preffnames - a list that is the same size as fields, gives another name for your fields
         objlist - list of a list (basically its a table of values you tell the "table.html" template to render
         request - request object
         searchdisp - prompt or instructions to the user
         user - user
         autocomplist - list of strings that you want to render as javascript
    """

    fields.insert(0,'#')
    if preffnames:
        preffnames.insert(0,'#')
    else:
        preffnames = fields

    if 'save' in request.POST:
        resp = HttpResponse(mimetype='text/csv')
        resp['Content-Disposition'] = 'attachment; filename=ngsdb_data.csv'
        writer = csv.writer(resp)
        writer.writerow(fields)
        for nrow in range(len(objlist)):
            writer.writerow(objlist[nrow])
    else:

        kwargs = {
            'autocomplist': autocomplist,
            'title': pagetitle,
            'user':user,
            'searchdisp': searchdisp,
            'form': form,
            'fields': preffnames,
            'list':objlist,
            'listoflinks':listoflinks,
        }

        #passes context to render in html file
        resp = render_to_response('ngsdbview/table.html', kwargs,context_instance=RequestContext(request))
    return resp


def getFieldsFrom(mod,preflist):
    """Function Name: getFieldsFrom
    Purpose: get fields from object mod
    """
    if preflist:
        return preflist

    newlist =[]
    #gets all the fields (side affect gets fields for foreign key models)
    modelattr =  mod._meta.get_all_field_names()
    #grabs an object of type model and checks if that field exists
    amodel = mod.objects.all()[0]
    for attr in modelattr:
        if getattr(amodel,attr,None):
            newlist.append(attr)

    return newlist

def combineQueries(queries):
    '''takes a list of Q objects and ORs them together into a single query'''
    query = queries.pop()
    for item in queries:
        query |= item
    return query

def constructAutocomplete(formfieldname,attrlist):
    ''' returns a string that can be rendered in the html template which should be used in a js environ'''

    #javascript command $("input#id_resultidfield").autocomplete({source: ["c++", "java", "php", "coldfusion", "javascript", "asp", "ruby"]});
    s = ['$("input#id_',formfieldname, '").autocomplete({source:[']

    for name in attrlist:
        s.append('"')
        s.append(str(name))
        s.append('",')

    s.append('""')
    s.append(']});')
    return ''.join(s)

def constructBarGraph(elid,xy,labels,ticks,title):
    '''
    Functiona Name: constructBarGraph
    Parameters:
        elid - document element id
        xy - set of a set of value points
        labels - name of each category
        ticks - overall series
        title - graph title
    Returns string to be renedered in html template and used in js environment'''
    s = []
    i = 1

    for aset in xy:
        s.append('var set' + str(i) + ' = [];')
        for x in aset:
            s.append('set' + str(i) + '.push(' + str(x) + ');')
        i = i+1

    s.append('var ticks =[')
    for atick in ticks:
        s.append('\'' + str(atick) + '\',')
        s.append('];')
        s.append('$.jqplot (\'' + str(elid)+ '\', ')
        s.append('[')
    i =1
    for aset in xy:
        s.append('set' + str(i) + ',')
        i = i+1

    s.append(']')

    s.append(', {seriesDefaults:{ renderer:$.jqplot.BarRenderer, rendererOptions:{fillToZero: true}},')
    s.append('series:[')
    for alabel in labels:
        s.append('{label:\'' + str(alabel) + '\'},')
    s.append('],')
    s.append('title: \''+str(title) + '\',')
    s.append('legend:{ show:true, placement: \'outsideGrid\'},')
    s.append('axes: {xaxis: {renderer:$.jqplot.CategoryAxisRenderer, ticks: ticks},')
    s.append('yaxis:{ pad: 1.05, tickOptions:{formatString: \'$%d\'}}}});')
    return ''.join(s)


def constructLineGraph(elid,xy,xyseriesnames,title,xlabel,ylabel):
    '''
    Functiona Name: constructLineGraph
    Parameters:
        elid - document element id
        xy - set of a set of x,y points
        xyseriesnames - name of each set of datapoints
        title - graph title
        xlabel - label of x-axis
        ylabel - label of y-axis
    Returns string to be renedered in html template and used in js environment'''


    s = []
    i = 1

    for aset in xy:
        s.append('var set' + str(i) + ' = [];')
        for x,y in aset:
            s.append('set' + str(i) + '.push([' + str(x) +','+ str(y)+']);')
        i = i+1

    s.append('$.jqplot (\'' + str(elid)+ '\', ')

    s.append('[')
    i =1
    for aset in xy:
        s.append('set' + str(i) + ',')
        i = i+1

    s.append(']')

    #s.append('[[3,7,9,1,4,6,8,2,5]]')
    s.append(', {title: \''+str(title) + '\',axesDefaults: {labelRenderer: $.jqplot.CanvasAxisLabelRenderer},')

    s.append('legend:{ show:true, labels:[')
    for sname in xyseriesnames:
        s.append('\''+ sname + '\',')
    s.append(']},')

    s.append('axes: {xaxis: {label: "' + str(xlabel) + '",pad: 0},yaxis: {label: "' + str(ylabel) + '"}}});')

    return ''.join(s)

def constructPieChart(elid,data,title):
    '''Function name: constructPiechart
    Parameters:
        elid - document element id
        data - list of datapoints i form ['label',value]
        title - title
        xlabel - label for x axis
        ylabel - label for y axis
    Returns string for constructing a pie chart to be renedered in html template and used in js environment
    '''
    s = [];
    s.append('var data = [')

    for ptlabel, no in data:
        s.append('[\'' + ptlabel + '\',' + str(no) + '],')

    s.append('];')

    s.append('$.jqplot (\'' + str(elid)+ '\', [data],')
    s.append('{title: \''+str(title) + '\',axesDefaults: {labelRenderer: $.jqplot.CanvasAxisLabelRenderer},')
    s.append('seriesDefaults:{renderer: jQuery.jqplot.PieRenderer,rendererOptions: {showDataLabels: true}},')
    s.append('legend: {show:true, location:\'e\'},')
    s.append('});')
    return ''.join(s)

def multiselectmenu(alist):
    '''renders a multiple select menu in an HTML environment'''
    s = []
    s.append('<select multiple="multiple">')

    for label in alist:
        s.append('<option value="' + str(label) + '">' + str(label) + '</option>')
    s.append('</select>')
    return ''.join(s)
