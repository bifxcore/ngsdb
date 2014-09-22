from django.contrib import admin
from snpdb.models import *


class ChromosomeAdmin(admin.ModelAdmin):
	list_display = ('chromosome_id', 'chromosome_name', 'size', 'genome_name', 'genome_version')
admin.site.register(Chromosome, ChromosomeAdmin)


class StatisticsAdmin(admin.ModelAdmin):
	list_display = ('stats_id', 'snp', 'stats_cvterm', 'cv_value')
admin.site.register(Statistics, StatisticsAdmin)


class EffectAdmin(admin.ModelAdmin):
	list_display = ('snp', 'effect', 'effect_class', 'effect_string', 'effect_group')
admin.site.register(Effect, EffectAdmin)


class FilterAdmin(admin.ModelAdmin):
	list_display = ('snp', 'filter_id', 'filter_result', 'filter_cv')
admin.site.register(Filter, FilterAdmin)


class FilterCVAdmin(admin.ModelAdmin):
	list_display = ('filter_cv_id', 'filter_type')
admin.site.register(Filter_CV, FilterCVAdmin)


class SNPAdmin(admin.ModelAdmin):
	list_display = ('snp_id', 'snp_position', 'result', 'ref_base', 'alt_base', 'heterozygosity', 'quality', 'library', 'chromosome')
admin.site.register(SNP, SNPAdmin)


class StatisticsCVAdmin(admin.ModelAdmin):
	list_display = ('stats_cvterm_id', 'cvterm', 'cv_notes')
admin.site.register(Statistics_cv, StatisticsCVAdmin)


class EffectCVAdmin(admin.ModelAdmin):
	list_display = ('effect_id', 'effect_name')
admin.site.register(Effect_CV, EffectCVAdmin)

class SNPTypeAdmin(admin.ModelAdmin):
	list_display = ('snptype_id', 'snp', 'indel', 'deletion', 'is_snp', 'monomorphic', 'transition', 'sv')
admin.site.register(SNP_Type, SNPTypeAdmin)


class SNPExternalDBReferenceAdmin(admin.ModelAdmin):
	list_display = ('snp', 'databaseReference_id', 'db_name', 'url')
admin.site.register(SNP_External_DBReference, SNPExternalDBReferenceAdmin)


class VcfFilesAdmin(admin.ModelAdmin):
	list_display = ('vcf_id', 'vcf_path', 'library', 'result', 'vcf_md5sum', 'date_uploaded', 'date_modified')
admin.site.register(VCF_Files, VcfFilesAdmin)