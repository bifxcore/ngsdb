#samples/tables.py
import django_tables2 as tables
from samples.models import *

class AuthorTable(tables.Table):
    class Meta:
        model = Author
        attrs = {"class": "paleblue"}



class LibraryTable(tables.Table):
    selection = tables.CheckBoxColumn(accessor="pk", orderable=False)
    is_clonal = tables.Column(verbose_name="Is clonal?")

    class Meta:
        model = Library
        fields = ("library_code", "librarytype", "collaborator", "author", "organism", "lifestage", "growthphase", "phenotype", "source", "treatment", "is_clonal", "flowcell_number")
        collaborator = tables.Column()
        author = tables.Column()
        sequence = ("selection", "library_code", "collaborator", "author" )
        attrs = {"class": "paleblue"}