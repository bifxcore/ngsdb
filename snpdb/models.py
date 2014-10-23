from django.db.models import *
from ngsdbview.models import *


class Chromosome(models.Model):
	chromosome_id = models.AutoField(primary_key=True)
	chromosome_name = models.CharField(max_length=50)
	size = models.IntegerField()
	genome_name = models.ForeignKey('ngsdbview.Organism', to_field='organismcode')
	genome_version = models.CharField(max_length=50)


#todo add index to effect_string
class Effect(models.Model):
	snp = models.ForeignKey('SNP')
	effect = models.ForeignKey('Effect_CV')
	effect_class = models.TextField(db_index=True)
	effect_string = models.TextField(db_index=True)
	effect_group = models.IntegerField()


class Effect_CV(models.Model):
	effect_id = models.AutoField(primary_key=True)
	effect_name = models.CharField(max_length=45, db_index=True)


class Filter(models.Model):
	snp = models.ForeignKey('SNP')
	filter_id = models.AutoField(primary_key=True)
	filter_result = models.BooleanField()
	filter_cv = models.ForeignKey('Filter_CV')


class Filter_CV(models.Model):
	filter_cv_id = models.AutoField(primary_key=True)
	filter_type = models.TextField(db_index=True)


class SNP(models.Model):
	snp_id = models.AutoField(primary_key=True)
	snp_position = models.IntegerField(db_index=True)
	result = models.ForeignKey('ngsdbview.Result')
	vcf = models.ForeignKey('VCF_Files')
	ref_base = models.TextField()
	alt_base = models.TextField()
	heterozygosity = NullBooleanField()
	quality = models.IntegerField()
	library = models.ForeignKey('samples.Library')
	chromosome = models.ForeignKey('Chromosome')
#    def __unicode__(self):
#        return str(self.snp_id)


class SNP_CV(models.Model):
	cv_id = models.AutoField(primary_key=True)
	cvterm = models.TextField(db_index=True)
	cv_value = models.TextField(db_index=True)


class SNP_Type(models.Model):
	snptype_id = models.AutoField(primary_key=True)
	snp = models.ForeignKey('SNP')
	indel = models.BooleanField()
	deletion = models.BooleanField()
	is_snp = models.BooleanField()
	monomorphic = models.BooleanField()
	transition = models.BooleanField()
	sv = models.BooleanField()


class Statistics_cv(models.Model):
	stats_cvterm_id = models.AutoField(primary_key=True)
	cvterm = models.CharField(max_length=50, unique=True, db_index=True)
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


class VCF_Files(models.Model):
	vcf_id = models.AutoField(primary_key=True)
	vcf_path = models.FileField(upload_to='VCF_Files', blank=True)
	library = models.ForeignKey('samples.Library')
	result = models.ForeignKey('ngsdbview.Result')
	vcf_md5sum = models.CharField(max_length=50, blank=True, null=True)
	date_uploaded = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)


class CNV(models.Model):
	cnv_id = models.AutoField(primary_key=True)
	chromosome = models.ForeignKey('Chromosome')
	start = models.IntegerField()
	stop = models.IntegerField()
	CNV_value = models.IntegerField()
	library = models.ForeignKey('samples.Library')
	result = models.ForeignKey('ngsdbview.Result')
	window_size = models.ForeignKey('CNV_CV')


class CNV_CV(models.Model):
	cv_id = models.AutoField(primary_key=True)
	cvterm = models.TextField(db_index=True)
	cv_value = models.TextField(db_index=True)