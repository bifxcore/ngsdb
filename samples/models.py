from django.db import models
from django.contrib.auth.models import User
from ngsdbview.models import Author, Organism, Lifestage, Phenotype, Librarytype, Collaborator, Growthphase, Genotype

# Create your models here.
TEMPLATE_MATERIALS_CHOICES = (
    ('TotalRNA', 'TotalRNA'),
    ('PolyApurified_mRNA', 'PolyApurified_mRNA'),
    ('gDNA', 'gDNA'),
    ('RibosomeBoundRNA', 'RibosomeBoundRNA')
)

class Genome(models.Model):
    reference_code = models.CharField(unique=True, max_length=10, help_text="Reference Genome Code")
    genus = models.CharField(max_length=45)
    species = models.CharField(max_length=45)
    strain = models.CharField(max_length=45, blank=True)
    isolate = models.CharField(max_length=45, blank=True)
    source = models.CharField(max_length=100, blank=True)
    dbxref = models.CharField(max_length=25, help_text="Genome Data Source")

    def __unicode__(self):
        return unicode(self.reference_code)

class Bioproject(models.Model):
    bioproject_code = models.CharField(unique=True, max_length=12)
    organisms = models.CharField(max_length=100, blank=True)
    sharepoint_projectcode = models.CharField(blank=True, max_length=12)
    notes = models.TextField(max_length=400, blank=True)

    def __unicode__(self):
        return unicode(self.bioproject_code)

class Biosample(models.Model):
    biosample_code = models.CharField(unique=True, max_length=12)
    organisms = models.CharField(max_length=100, blank=True)
    notes = models.TextField(max_length=400, blank=True)

    def __unicode__(self):
        return unicode(self.biosample_code)

class Protocol(models.Model):
    protocol_name = models.CharField(unique=True, max_length=50)
    protocol_file = models.FileField(upload_to="protocols", blank=True)
    protocol_link = models.URLField(max_length=1000, blank=True)
    notes = models.CharField(max_length=400, default=None)
    def __unicode__(self):
        return unicode(self.protocol_name)


class Library(models.Model):
    library_code = models.CharField(max_length=10, db_index=True, unique=True, blank=True, help_text="Only Settle BioMed\'s internal users may use this. eg. ES001, AH002")
    author = models.ForeignKey('ngsdbview.Author', related_name="ngsdbview.authors", help_text="Person constructed the library")
    collaborator = models.ForeignKey('ngsdbview.Collaborator', related_name="ngsdbview.collaborator", help_text="Initials of the PI collaborating on this project")
    bioproject = models.ForeignKey(Bioproject, help_text="Bioproject ID from NCBI")
    biosample = models.ForeignKey(Biosample, help_text="Biosample ID from NCBI")
    sample_name = models.CharField(max_length=25, db_index=True, blank=True, help_text="Sample name from the source")
    sample_id = models.CharField(max_length=25, db_index=True, blank=True, help_text="Sample id from the source")
    organism = models.ForeignKey('ngsdbview.Organism', related_name="ngsdbview.organism", help_text="The organism sample data derived from")
    lifestage = models.ForeignKey('ngsdbview.Lifestage', related_name="ngsdbview.lifestage", help_text="Eg., Promastigotes, 10hrs, amastigotes etc")
    growthphase = models.ForeignKey('ngsdbview.Growthphase', related_name="ngsdbview.growthphase", help_text="Eg., procyclic, log")
    phenotype = models.ForeignKey('ngsdbview.Phenotype', related_name="ngsdbview.phenotype", help_text="Eg., Wildtype, Dwarf or Iron depletion etc")
    genotype = models.ForeignKey('ngsdbview.Genotype', related_name="ngsdbview.genotype", help_text="Eg., Wildtype, JBP2KO")
    source = models.CharField(max_length=100, help_text="Eg., Subcutaneous Leishion of an adult male, Lab culture, chimeric mouse liver")
    treatment = models.CharField(max_length=100, help_text="BrdU treatment for 5 hrs")
    collected_on = models.DateField(null=True, blank=True)
    collected_at = models.CharField(max_length=100, blank=True, help_text="Brazil or Bihar, India")
    collected_by = models.CharField(max_length=50, blank=True, help_text="Name of the person collected")
    sample_notes = models.TextField(help_text="Any other information related to sample, sample collection etc")
    is_clonal = models.BooleanField(default=False, help_text="Are the cells cloned to single cell before growing for this library?")

    librarytype = models.ForeignKey('ngsdbview.Librarytype', related_name="ngsdbview.librarytype", help_text="Type of library to be constructed")
    template_material = models.CharField(max_length=200, choices=TEMPLATE_MATERIALS_CHOICES)
    protocol = models.ForeignKey(Protocol, help_text="Add a new protocol using '+' before selecting here. Use the Protocol additional notes to describe any changes in protocol")
    protocol_notes = models.TextField(blank=True, default="None")

    library_creation_date = models.DateField(blank=True, null=True)
    submitted_for_sequencing_on = models.DateField(blank=True, null=True)
    sequence_downloaded_on = models.DateField(blank=True, null=True)
    flowcell_number = models.CharField(max_length=15, blank=True)
    lane_number = models.CharField(max_length=3, blank=True)
    index_sequence = models.CharField(max_length=25, blank=True)
    experiment_notes = models.TextField(blank=True,)

    reference_genome = models.ForeignKey(Genome,  help_text="Name of genome to align against")
    reference_genome_version = models.CharField(max_length=50,  blank=True, default="Latest")
    note_for_analysis = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    author_modified = models.ForeignKey(User)
    def __unicode__(self):
        return unicode(self.library_code)

