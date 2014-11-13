from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from ngsdbview.models import *

from django import forms
from django.forms.models import BaseInlineFormSet

from ngsdbview.autoregister import autoregister

admin.site.unregister(User)
class UserProfileInline(admin.StackedInline):
    model = UserProfile

class UserProfileAdmin(UserAdmin):
    inlines = [ UserProfileInline, ]
admin.site.register(User, UserProfileAdmin)

#admin.site.register(Library)

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'designation', 'email')
admin.site.register(Author, AuthorAdmin)

class CollaboratorAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'affiliation', 'email')
admin.site.register(Collaborator, CollaboratorAdmin)

class FeatureAdmin(admin.ModelAdmin):
    list_display = ('genome', 'geneid', 'geneproduct', 'annotation')
    search_fields = ['geneid', 'geneproduct', 'annotation']
    list_filter = ['genome']
admin.site.register(Feature, FeatureAdmin)

class GenomeAdmin(admin.ModelAdmin):
    list_display = ('genome_id', 'organism', 'version', 'source')
admin.site.register(Genome, GenomeAdmin)

class OrganismAdmin(admin.ModelAdmin):
    list_display = ('organismcode', 'genus', 'species', 'strain')
admin.site.register(Organism, OrganismAdmin)

class SoftwareAdmin(admin.ModelAdmin):
    list_display = ('software_id', 'name', 'version', 'algorithm', 'source', 'sourceuri')
admin.site.register(Software, SoftwareAdmin)


# code for editing Resultfile/Resultprop while in Library admin page
class ResultfileInline(admin.TabularInline):
    model = Resultfile
class ResultpropInline(admin.TabularInline):
    model = Resultprop

class ResultAdmin(admin.ModelAdmin):
    inlines = [ ResultfileInline, ResultpropInline ]
admin.site.register(Result, ResultAdmin)


# code for editing Analysisfile/Analyisprop while in Library admin page
class AnalysisfileInline(admin.TabularInline):
    model = Analysisfile

class AnalysispropInline(admin.TabularInline):
    model = Analysisprop

class AnalysisAdmin(admin.ModelAdmin):
    inlines = [ AnalysisfileInline, AnalysispropInline ]
admin.site.register(Analysis, AnalysisAdmin)


class ProtocolAdmin(admin.ModelAdmin):
    list_display = ('protocol_name', 'protocol_file', 'protocol_link', 'notes')
admin.site.register(Protocol, ProtocolAdmin)


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'type', 'refgenome', 'description', 'date_modified')
admin.site.register(Experiment, ExperimentAdmin)

class ExptfileAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'category', 'subcategory', 'file')
admin.site.register(Exptfile, ExptfileAdmin)

class ExptsetupAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'groupname', 'notes')
admin.site.register(Exptsetup, ExptsetupAdmin)

class ComparisonAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'compname', 'basegroup', 'querygroup', 'description')
admin.site.register(Comparison, ComparisonAdmin)

class CompfileAdmin(admin.ModelAdmin):
    list_display = ('comparison', 'category', 'subcategory', 'file')
admin.site.register(Compfile, CompfileAdmin)

class DiffexpnAdmin(admin.ModelAdmin):
    list_display = ('feature', 'experiment', 'compname', 'log2foldchange', 'pvalue', 'fdr')
admin.site.register(Diffexpn, DiffexpnAdmin)


class TagcountAmin(admin.ModelAdmin):
    list_display = ("feature", "library", "rawcount", "normalizedcount", "experiment")
admin.site.register(Tagcount, TagcountAmin)

autoregister('ngsdbview')
