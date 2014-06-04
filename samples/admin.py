from django.contrib import admin
from samples.models import *
from django.forms import forms
from django.contrib import admin



class SampleAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Sample', {'fields':('sampleid', 'sampletype', 'collaborator', 'label_ontube')}),
        ('Sample Source Information', {'fields':('organism', 'genotype', 'lifestage', 'growthphase', 'phenotype', 'culture_method', 'treatment', 'time_after_treatment', 'is_clonal', 'source', 'sourcename'), 'classes': ('grp-collapse grp-close',),}),
        ('Sample Isolation Information', {'fields':('isolation_method', 'collected_on', 'collected_by', 'collected_by_emailid'), 'classes': ('grp-collapse grp-close',),}),
        ('Storage Information', {'fields':('date_received', 'sample_concentration', 'sample_volume', 'sample_quantity', 'parent_sampleid', 'sample_dilution', 'freezer_location', 'biological_replicate_of'), 'classes': ('grp-collapse grp-close',),}),
        ('Other/QC Information', {'fields':('bioanalyzer_analysis', 'sample_notes', 'author_modified'), 'classes': ('grp-collapse grp-close',),}),
    )

    list_display = ('sampleid', 'sampletype', 'organism', 'lifestage', 'genotype', 'collaborator', 'growthphase', 'treatment', 'time_after_treatment', 'sample_quantity', 'bioanalyzer_file_link', 'label_ontube', 'freezer_location', 'sample_notes')
    list_filter = ['sampletype', 'organism', 'lifestage', 'collaborator', 'treatment']
    search_fields = ['sampleid', 'sampletype', 'organism__organismcode', 'lifestage__lifestage', 'growthphase__growthphase', 'phenotype__phenotype', 'genotype__genotype', 'collaborator__firstname', 'collaborator__lastname', 'source', 'collected_by', 'treatment', 'isolation_method', 'sample_quantity', 'biological_replicate_of', 'bioanalyzer_analysis', 'label_ontube', 'freezer_location', 'sample_notes']
admin.site.register(Sample, SampleAdmin)

class LibraryAdmin(admin.ModelAdmin):
    readonly_fields = ("date_modified", "date_created")

    fieldsets = (
        ('Library', {'fields':('library_code', 'author', 'collaborator')}),
        ('Sample Information', {'fields': ('sampleid', 'biosample', 'bioproject'), 'classes': ('grp-collapse grp-open',), }),
        ('Library Construction', {'fields': ('librarytype', 'template_material', 'protocol', 'protocol_notes', 'library_creation_date', 'submitted_for_sequencing_on', 'library_gelimage'), 'classes': ('grp-collapse grp-open',), }),
        ('Sequencing Information', {'fields': ('sequence_downloaded_on', 'flowcell_number', 'lane_number', 'index_sequence', 'fastqfile_name', 'fastqfile_readcount', 'fastqfile_size_inbytes', 'fastqfile_md5sum', 'experiment_notes'), 'classes': ('grp-collapse grp-open',), }),
        ('Analysis Information', {'fields': ('reference_genome', 'reference_genome_version', 'note_for_analysis'), 'classes': ('grp-collapse grp-open',), }),
        ('Data Tracking', {'fields': ('date_created', 'date_modified', 'author_modified'), 'classes': ('grp-collapse grp-open',), })
    )

    list_display = ('library_code', 'sampleid', 'librarytype', 'organism', 'lifestage', 'phenotype', 'genotype', 'growthphase', 'treatment', 'template_material', 'reference_genome', 'collaborator', 'bioproject', 'library_creation_date', 'sequence_downloaded_on', 'flowcell_number','lane_number', 'index_sequence', 'fastqfile_name')
    list_filter = ['collaborator', 'librarytype__type', 'author__designation', 'organism__organismcode', 'lifestage', 'phenotype', 'genotype', 'growthphase', 'template_material', 'reference_genome' ]
    search_fields = ['collaborator__firstname', 'rna_id', 'collaborator__lastname', 'librarytype__type', 'author__designation', 'author__lastname', 'author__firstname', 'organism__organismcode', 'organism__species', 'organism__genus', 'experiment_notes', 'sample_notes',  'protocol_notes', 'lifestage__lifestage', 'growthphase__growthphase', 'phenotype__phenotype', 'genotype__genotype',  'bioproject__bioproject_code', 'bioproject__bioproject_code', 'biosample__biosample_code', 'protocol__protocol_name', 'library_code', 'flowcell_number', 'index_sequence']

admin.site.register(Library, LibraryAdmin)


class BioprojctAdmin(admin.ModelAdmin):

    list_display=('bioproject_code', 'organisms', 'notes')

admin.site.register(Bioproject, BioprojctAdmin)

class BiosampleAdmin(admin.ModelAdmin):
    list_display=('biosample_code', 'organisms', 'notes')
admin.site.register(Biosample, BiosampleAdmin)

admin.site.register(Protocol)
admin.site.register(Source)
admin.site.register(Genome)



