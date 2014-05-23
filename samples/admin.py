from django.contrib import admin
from samples.models import *
from django.forms import forms
from django.contrib import admin



class LibraryAdmin(admin.ModelAdmin):
    #def save_model(self, request, obj, form, change):

        #Over rides default save_model() to insert logged in user from User table (request.user)
        #get inserted into author_modified

        #if getattr(obj, 'author', None) is None:
        #    obj.author_modified = request.user
        #obj.save()

    # format the display in the admin form #for individual gene
    readonly_fields = ("date_modified", "date_created")

    fieldsets = (
        ('Library', {'fields':('library_code', 'author', 'collaborator', 'bioproject')}),
        ('Sample Information', {'fields': ('sample_name', 'rna_id','biosample', 'organism', 'lifestage', 'growthphase', 'phenotype', 'genotype', 'source', 'treatment', 'collected_on', 'collected_at', 'collected_by', 'sample_notes', 'is_clonal'), 'classes': ('grp-collapse grp-open',), }),
        ('Library Construction', {'fields': ('librarytype', 'template_material', 'protocol', 'protocol_notes', 'library_creation_date', 'submitted_for_sequencing_on'), 'classes': ('grp-collapse grp-open',), }),
        ('Sequencing Information', {'fields': ('sequence_downloaded_on', 'flowcell_number', 'lane_number', 'index_sequence', 'experiment_notes'), 'classes': ('grp-collapse grp-open',), }),
        ('Analysis Information', {'fields': ('reference_genome', 'reference_genome_version', 'note_for_analysis'), 'classes': ('grp-collapse grp-open',), }),
        ('Data Tracking', {'fields': ('date_created', 'date_modified', 'author_modified'), 'classes': ('grp-collapse grp-open',), })
    )

    list_display = ('library_code', 'sample_name', 'librarytype', 'organism', 'lifestage', 'phenotype', 'genotype', 'growthphase', 'treatment', 'template_material', 'reference_genome', 'collaborator', 'bioproject', 'sample_name', 'rna_id', 'library_creation_date', 'sequence_downloaded_on', 'flowcell_number','lane_number', 'index_sequence')
    list_filter = ['collaborator', 'librarytype__type', 'author__designation', 'organism__organismcode', 'lifestage', 'phenotype', 'genotype', 'growthphase', 'template_material', 'reference_genome', ]
    search_fields = ['collaborator__firstname', 'rna_id', 'collaborator__lastname', 'librarytype__type', 'author__designation', 'author__lastname', 'author__firstname', 'organism__organismcode', 'organism__species', 'organism__genus', 'experiment_notes', 'sample_notes',  'protocol_notes', 'lifestage__lifestage', 'growthphase__growthphase', 'phenotype__phenotype', 'genotype__genotype',  'bioproject__bioproject_code', 'bioproject__bioproject_code', 'biosample__biosample_code', 'protocol__protocol_name', 'library_code', 'flowcell_number', 'index_sequence',]

admin.site.register(Library, LibraryAdmin)

admin.site.register(Genome)
admin.site.register(Bioproject)
admin.site.register(Biosample)
admin.site.register(Protocol)


