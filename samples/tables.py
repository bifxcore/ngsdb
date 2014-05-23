#samples/tables.py
import django_tables2 as tables
from django_tables2_reports.tables import TableReport
from samples.models import *

class AuthorTable(TableReport):
    class Meta:
        model = Author
        attrs = {"class": "paleblue"}




class LibraryTable(TableReport):
    selection = tables.CheckBoxColumn(accessor="pk", orderable=False)
    is_clonal = tables.Column(verbose_name="Is clonal?")
    date_modified = tables.DateColumn()
    collaborator = tables.Column()
    author = tables.Column()

    class Meta:
        model = Library
        fields = ("library_code", "sample_name", "librarytype", "collaborator", "author", "organism", "lifestage", "growthphase", "phenotype", "source", "treatment", "is_clonal", "flowcell_number", "date_modified")
        sequence = ("selection", "library_code", "collaborator", "author" )
        attrs = {"class": "paleblue"}


