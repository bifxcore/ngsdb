from django.contrib import admin
from snpdb.models import *


class ChromosomeAdmin(admin.ModelAdmin):
    list_display = ('chromosome_id', 'chromosome_name', 'size', 'genome_name', 'genome_version')
admin.site.register(Chromosome, ChromosomeAdmin)


class Statistics_cvsAdmin(admin.ModelAdmin):
    list_display = ('stats_cvterm_id', 'cvterm', 'cv_notes')
admin.site.register(Statistics_cv, Statistics_cvsAdmin)


class StatisticsAdmin(admin.ModelAdmin):
    list_display = ('stats_id', 'snp', 'stats_cvterm', 'cv_value')
admin.site.register(Statistics, StatisticsAdmin)
