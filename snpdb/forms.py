from django import forms
from snpdb.models import *
#from materials.viewtools import *

class CnvFilterForm(forms.Form):
    librarycode = forms.CharField()
    normalrange_mincnv = forms.FloatField()
    normalrange_maxcnv = forms.FloatField()