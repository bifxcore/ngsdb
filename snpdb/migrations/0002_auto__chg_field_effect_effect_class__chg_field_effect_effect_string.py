# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Effect.effect_class'
        db.alter_column(u'snpdb_effect', 'effect_class', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Effect.effect_string'
        db.alter_column(u'snpdb_effect', 'effect_string', self.gf('django.db.models.fields.TextField')())

    def backwards(self, orm):

        # Changing field 'Effect.effect_class'
        db.alter_column(u'snpdb_effect', 'effect_class', self.gf('django.db.models.fields.CharField')(max_length=45))


        # Changing field 'Effect.effect_string'
        db.alter_column(u'snpdb_effect', 'effect_string', self.gf('django.db.models.fields.CharField')(max_length=45))

    models = {
        u'ngsdbview.author': {
            'Meta': {'object_name': 'Author'},
            'author_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'designation': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '5'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '45'})
        },
        u'ngsdbview.collaborator': {
            'Meta': {'object_name': 'Collaborator'},
            'affiliation': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'collaborator_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '100'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'ftp_path': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'ftp_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'sharepoint_site': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'ngsdbview.genome': {
            'Meta': {'object_name': 'Genome'},
            'genome_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Organism']"}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'svnpath': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'svnrevision': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '45'})
        },
        u'ngsdbview.library': {
            'Meta': {'object_name': 'Library'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Author']"}),
            'collaborator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Collaborator']"}),
            'downloaddate': ('django.db.models.fields.DateField', [], {}),
            'fastqalias': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'fastqname': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'fastqpath': ('django.db.models.fields.CharField', [], {'max_length': '1025'}),
            'flowcell': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'library_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'librarycode': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25', 'db_index': 'True'}),
            'librarysize': ('django.db.models.fields.IntegerField', [], {}),
            'librarytype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Librarytype']"}),
            'lifestage': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Lifestage']"}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'organism': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Organism']"}),
            'phenotype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Phenotype']"}),
            'protocol': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Protocol']"}),
            'samplename': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '25', 'blank': 'True'})
        },
        u'ngsdbview.librarytype': {
            'Meta': {'object_name': 'Librarytype'},
            'librarytype_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '400', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25'})
        },
        u'ngsdbview.lifestage': {
            'Meta': {'ordering': "['lifestage']", 'object_name': 'Lifestage'},
            'lifestage': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '45'}),
            'lifestage_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '400'})
        },
        u'ngsdbview.organism': {
            'Meta': {'object_name': 'Organism'},
            'genus': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'organism_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organismcode': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'species': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'strain': ('django.db.models.fields.CharField', [], {'max_length': '45'})
        },
        u'ngsdbview.phenotype': {
            'Meta': {'object_name': 'Phenotype'},
            'notes': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '45'}),
            'phenotype': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '45'}),
            'phenotype_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'ngsdbview.protocol': {
            'Meta': {'ordering': "['protocol_name']", 'object_name': 'Protocol'},
            'notes': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '400'}),
            'protocol_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'protocol_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'protocol_link': ('django.db.models.fields.URLField', [], {'max_length': '1000', 'blank': 'True'}),
            'protocol_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'ngsdbview.result': {
            'Meta': {'object_name': 'Result'},
            'analysispath': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Author']"}),
            'genome': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Genome']"}),
            'is_current': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_obsolete': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'libraries': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ngsdbview.Library']", 'symmetrical': 'False'}),
            'notes': ('django.db.models.fields.TextField', [], {'default': 'None'}),
            'result_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_data_loaded': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'snpdb.chromosome': {
            'Meta': {'object_name': 'Chromosome'},
            'chromosome_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'chromosome_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'genome_name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Organism']", 'to_field': "'organismcode'"}),
            'genome_version': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'size': ('django.db.models.fields.IntegerField', [], {})
        },
        u'snpdb.effect': {
            'Meta': {'object_name': 'Effect'},
            'effect': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.Effect_CV']"}),
            'effect_class': ('django.db.models.fields.TextField', [], {}),
            'effect_group': ('django.db.models.fields.IntegerField', [], {}),
            'effect_string': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'snp': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.SNP']"})
        },
        u'snpdb.effect_cv': {
            'Meta': {'object_name': 'Effect_CV'},
            'effect_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'effect_name': ('django.db.models.fields.CharField', [], {'max_length': '45'})
        },
        u'snpdb.filter': {
            'Meta': {'object_name': 'Filter'},
            'filter_cv': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.Filter_CV']"}),
            'filter_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'filter_result': ('django.db.models.fields.BooleanField', [], {}),
            'snp': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.SNP']"})
        },
        u'snpdb.filter_cv': {
            'Meta': {'object_name': 'Filter_CV'},
            'filter_cv_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'filter_type': ('django.db.models.fields.TextField', [], {})
        },
        u'snpdb.snp': {
            'Meta': {'object_name': 'SNP'},
            'alt_base': ('django.db.models.fields.TextField', [], {}),
            'chromosome': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.Chromosome']"}),
            'heterozygosity': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'library': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Library']"}),
            'quality': ('django.db.models.fields.IntegerField', [], {}),
            'ref_base': ('django.db.models.fields.TextField', [], {}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Result']"}),
            'snp_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'snp_position': ('django.db.models.fields.IntegerField', [], {})
        },
        u'snpdb.snp_external_dbreference': {
            'Meta': {'object_name': 'SNP_External_DBReference'},
            'databaseReference_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'db_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'snp': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.SNP']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'snpdb.snp_summary': {
            'Meta': {'object_name': 'SNP_Summary'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.Summary_Level_CV']"}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Result']"}),
            'tag': ('django.db.models.fields.TextField', [], {}),
            'value': ('django.db.models.fields.TextField', [], {}),
            'value_type': ('django.db.models.fields.TextField', [], {})
        },
        u'snpdb.snp_type': {
            'Meta': {'object_name': 'SNP_Type'},
            'deletion': ('django.db.models.fields.BooleanField', [], {}),
            'indel': ('django.db.models.fields.BooleanField', [], {}),
            'is_snp': ('django.db.models.fields.BooleanField', [], {}),
            'monomorphic': ('django.db.models.fields.BooleanField', [], {}),
            'snp': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.SNP']"}),
            'snptype_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sv': ('django.db.models.fields.BooleanField', [], {}),
            'transition': ('django.db.models.fields.BooleanField', [], {})
        },
        u'snpdb.statistics': {
            'Meta': {'object_name': 'Statistics'},
            'cv_value': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'snp': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.SNP']"}),
            'stats_cvterm': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.Statistics_cv']", 'to_field': "'cvterm'"}),
            'stats_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'snpdb.statistics_cv': {
            'Meta': {'object_name': 'Statistics_cv'},
            'cv_notes': ('django.db.models.fields.TextField', [], {}),
            'cvterm': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'stats_cvterm_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'snpdb.summary_level_cv': {
            'Meta': {'object_name': 'Summary_Level_CV'},
            'level_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level_name': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        }
    }

    complete_apps = ['snpdb']
