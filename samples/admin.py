from django.contrib import admin
from samples.models import *
from django.forms import forms
from django.contrib import admin
from django.contrib.auth.models import User



class SampleAdmin(admin.ModelAdmin):
    readonly_fields = ("author_modified", "date_modified")
    fieldsets = (
        ('Sample', {'fields':('sampleid', 'sampletype', 'collaborator', 'label_ontube', 'biosample')}),
        ('Sample Source Information', {'fields':('organism', 'genotype', 'lifestage', 'growthphase', 'phenotype', 'is_clonal', 'culture_method', 'treatment', 'time_after_treatment', 'source', 'sourcename'), 'classes': ('grp-collapse grp-close',),}),
        ('Sample Isolation Information', {'fields':('isolation_method', 'collected_at', 'collected_on', 'collected_by', 'collected_by_emailid'), 'classes': ('grp-collapse grp-close',),}),
        ('Storage Information', {'fields':('date_received', 'sample_concentration', 'sample_volume', 'sample_quantity', 'parent_sampleid', 'sample_dilution', 'freezer_location', 'biological_replicate_of'), 'classes': ('grp-collapse grp-close',),}),
        ('Other/QC Information', {'fields':('bioanalyzer_analysis', 'sample_notes', 'author_modified'), 'classes': ('grp-collapse grp-close',),}),
    )

    list_display = ('sampleid', 'sampletype', 'biosample', 'collaborator', 'organism', 'lifestage', 'genotype', 'growthphase', 'culture_method', 'treatment', 'time_after_treatment', 'sample_quantity', 'bioanalyzer_file_link', 'label_ontube', 'freezer_location')
    list_filter = ['sampletype', 'organism', 'lifestage', 'collaborator', 'treatment']
    search_fields = ['sampleid', 'biosample__biosample_code', 'sampletype', 'organism__organismcode', 'lifestage__lifestage', 'growthphase__growthphase', 'phenotype', 'genotype__genotype', 'collaborator__firstname', 'collaborator__lastname', 'source', 'collected_by', 'treatment', 'isolation_method', 'sample_quantity', 'biological_replicate_of', 'bioanalyzer_analysis', 'label_ontube', 'freezer_location', 'sample_notes']
    list_editable = ('growthphase', 'culture_method', 'lifestage', 'treatment', 'time_after_treatment')
    # todo remove editable list once aarthi is done

    def save_model(self, request, obj, form, change):
        obj.author_modified = request.user
        obj.save()

admin.site.register(Sample, SampleAdmin)

class LibraryAdmin(admin.ModelAdmin):
    readonly_fields = ("date_modified", "date_created", "author_modified")

    #fieldsets = (
    #    ('Library', {'fields':('library_code', 'author', 'collaborator')}),
    #    ('Sample Information', {'fields': ('sampleid', 'biosample', 'bioproject'), 'classes': ('grp-collapse grp-close',), }),
    #    ('Library Construction', {'fields': ('librarytype', 'template_material', 'protocol', 'protocol_notes', 'library_creation_date', 'submitted_for_sequencing_on', 'library_gelimage'), 'classes': ('grp-collapse grp-close',), }),
    #    ('Sequencing Information', {'fields': ('sequence_downloaded_on', 'flowcell_number', 'lane_number', 'index_sequence', 'fastqfile_name', 'fastqfile_readcount', 'fastqfile_size_inbytes', 'fastqfile_md5sum', 'experiment_notes'), 'classes': ('grp-collapse grp-close',), }),
    #    ('Analysis Information', {'fields': ('suggested_reference_genome', 'note_for_analysis'), 'classes': ('grp-collapse grp-close',), }),
    #    ('Data Tracking', {'fields': ('date_created', 'date_modified', 'author_modified'), 'classes': ('grp-collapse grp-close',), })
    #)
    list_display = ('library_code', 'sampleid', 'librarytype', 'protocol', 'template_material', 'suggested_reference_genome', 'collaborator', 'bioproject', 'library_creation_date', 'sequence_downloaded_on', 'flowcell_number', 'lane_number', 'index_sequence', 'fastqfile_name', 'fastqfile_readcount')
    list_filter = ['collaborator', 'librarytype__type', 'author__designation', 'template_material', 'suggested_reference_genome']
    search_fields = ['collaborator__firstname', 'collaborator__lastname', 'librarytype__type', 'author__designation', 'author__lastname', 'author__firstname', 'experiment_notes', 'protocol_notes', 'bioproject__bioproject_code', 'protocol__protocol_name', 'library_code', 'flowcell_number', 'index_sequence']
    list_editable = ('protocol', 'template_material')
    # todo remove editable list once aarthi is done
    # todo uncomment after all uploading of libraries

    def save_model(self, request, obj, form, change):
        obj.author_modified = request.user
        obj.save()

admin.site.register(Library, LibraryAdmin)


class BioprojctAdmin(admin.ModelAdmin):

    list_display=('bioproject_code', 'organisms', 'notes')

admin.site.register(Bioproject, BioprojctAdmin)

class BiosampleAdmin(admin.ModelAdmin):
    list_display=('biosample_code', 'organisms', 'notes')
admin.site.register(Biosample, BiosampleAdmin)



# class GenomeAdmin(admin.ModelAdmin):
#     list_display=('reference_code', 'genus', 'species', 'strain')
# admin.site.register(Genome, GenomeAdmin)

admin.site.register(Source)



