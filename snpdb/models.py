from django.db.models import *
from ngsdbview.models import *


class Chromosome(models.Model):
    chromosome_id = models.AutoField(primary_key=True)
    chromosome_name = models.CharField(max_length=50)
    size = models.IntegerField()
    genome_name = models.ForeignKey('ngsdbview.Organism', to_field='organismcode')
    genome_version = models.CharField(max_length=50)


class Effect(models.Model):
    snp = models.ForeignKey('SNP')
    effect = models.ForeignKey('Effect_CV')
    effect_class = models.CharField(max_length=45)
    effect_string = models.CharField(max_length=45)
    effect_group = models.IntegerField()


class Effect_CV(models.Model):
    effect_id = models.AutoField(primary_key=True)
    effect_name = models.CharField(max_length=45)


class Filter(models.Model):
    snp = models.ForeignKey('SNP')
    filter_id = models.AutoField(primary_key=True)
    filter_result = models.BooleanField()
    filter_cv = models.ForeignKey('Filter_CV')


class Filter_CV(models.Model):
    filter_cv_id = models.AutoField(primary_key=True)
    filter_type = models.TextField()


class SNP(models.Model):
    snp_id = models.AutoField(primary_key=True)
    snp_position = models.IntegerField()
    result = models.ForeignKey('ngsdbview.Result')
    ref_base = models.TextField()
    alt_base = models.TextField()
    heterozygosity = NullBooleanField()
    quality = models.IntegerField()
    library = models.ForeignKey('ngsdbview.Library')
    chromosome = models.ForeignKey('Chromosome')
#    def __unicode__(self):
#        return str(self.snp_id)


class SNP_Summary(models.Model):
    result = models.ForeignKey('ngsdbview.Result')
    level = models.ForeignKey('Summary_Level_CV')
    tag = models.TextField()
    value_type = models.TextField()
    value = models.TextField()


class SNP_Type(models.Model):
    snptype_id = models.AutoField(primary_key=True)
    snp = models.ForeignKey('SNP')
    indel = models.BooleanField()
    deletion = models.BooleanField()
    is_snp = models.BooleanField()
    monomorphic = models.BooleanField()
    transition = models.BooleanField()
    sv = models.BooleanField()


class Summary_Level_CV(models.Model):
    level_id = models.AutoField(primary_key=True)
    level_name = models.CharField(max_length=25)


class Statistics_cv(models.Model):
    stats_cvterm_id = models.AutoField(primary_key=True)
    cvterm = models.CharField(max_length=50, unique=True)
    cv_notes = models.TextField()


class Statistics(models.Model):
    stats_id = models.AutoField(primary_key=True)
    snp = models.ForeignKey('SNP', on_delete=models.CASCADE)
    stats_cvterm = models.ForeignKey('Statistics_cv', to_field='cvterm')
    cv_value = models.CharField(max_length=50)

class SNP_External_DBReference(models.Model):
    snp = models.ForeignKey('SNP')
    databaseReference_id = models.AutoField(primary_key=True)
    db_name = models.CharField(max_length=50)
    url = models.CharField(max_length=100)