# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Chromosome'
        db.create_table(u'snpdb_chromosome', (
            ('chromosome_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('chromosome_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
            ('genome_name', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ngsdbview.Organism'], to_field='organismcode')),
            ('genome_version', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'snpdb', ['Chromosome'])

        # Adding model 'Effect'
        db.create_table(u'snpdb_effect', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('snp', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['snpdb.SNP'])),
            ('effect', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['snpdb.Effect_CV'])),
            ('effect_class', self.gf('django.db.models.fields.CharField')(max_length=45)),
            ('effect_string', self.gf('django.db.models.fields.CharField')(max_length=45)),
            ('effect_group', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'snpdb', ['Effect'])

        # Adding model 'Effect_CV'
        db.create_table(u'snpdb_effect_cv', (
            ('effect_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('effect_name', self.gf('django.db.models.fields.CharField')(max_length=45)),
        ))
        db.send_create_signal(u'snpdb', ['Effect_CV'])

        # Adding model 'Filter'
        db.create_table(u'snpdb_filter', (
            ('snp', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['snpdb.SNP'])),
            ('filter_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filter_result', self.gf('django.db.models.fields.BooleanField')()),
            ('filter_cv', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['snpdb.Filter_CV'])),
        ))
        db.send_create_signal(u'snpdb', ['Filter'])

        # Adding model 'Filter_CV'
        db.create_table(u'snpdb_filter_cv', (
            ('filter_cv_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filter_type', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'snpdb', ['Filter_CV'])

        # Adding model 'SNP'
        db.create_table(u'snpdb_snp', (
            ('snp_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('snp_position', self.gf('django.db.models.fields.IntegerField')()),
            ('result', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ngsdbview.Result'])),
            ('ref_base', self.gf('django.db.models.fields.TextField')()),
            ('alt_base', self.gf('django.db.models.fields.TextField')()),
            ('heterozygosity', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('quality', self.gf('django.db.models.fields.IntegerField')()),
            ('library', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ngsdbview.Library'])),
            ('chromosome', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['snpdb.Chromosome'])),
        ))
        db.send_create_signal(u'snpdb', ['SNP'])

        # Adding model 'SNP_Summary'
        db.create_table(u'snpdb_snp_summary', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('result', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ngsdbview.Result'])),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['snpdb.Summary_Level_CV'])),
            ('tag', self.gf('django.db.models.fields.TextField')()),
            ('value_type', self.gf('django.db.models.fields.TextField')()),
            ('value', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'snpdb', ['SNP_Summary'])

        # Adding model 'SNP_Type'
        db.create_table(u'snpdb_snp_type', (
            ('snptype_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('snp', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['snpdb.SNP'])),
            ('indel', self.gf('django.db.models.fields.BooleanField')()),
            ('deletion', self.gf('django.db.models.fields.BooleanField')()),
            ('is_snp', self.gf('django.db.models.fields.BooleanField')()),
            ('monomorphic', self.gf('django.db.models.fields.BooleanField')()),
            ('transition', self.gf('django.db.models.fields.BooleanField')()),
            ('sv', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'snpdb', ['SNP_Type'])

        # Adding model 'Summary_Level_CV'
        db.create_table(u'snpdb_summary_level_cv', (
            ('level_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('level_name', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal(u'snpdb', ['Summary_Level_CV'])

        # Adding model 'Statistics_cv'
        db.create_table(u'snpdb_statistics_cv', (
            ('stats_cvterm_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cvterm', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('cv_notes', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'snpdb', ['Statistics_cv'])

        # Adding model 'Statistics'
        db.create_table(u'snpdb_statistics', (
            ('stats_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('snp', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['snpdb.SNP'])),
            ('stats_cvterm', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['snpdb.Statistics_cv'], to_field='cvterm')),
            ('cv_value', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'snpdb', ['Statistics'])

        # Adding model 'SNP_External_DBReference'
        db.create_table(u'snpdb_snp_external_dbreference', (
            ('snp', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['snpdb.SNP'])),
            ('databaseReference_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('db_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'snpdb', ['SNP_External_DBReference'])


    def backwards(self, orm):
        # Deleting model 'Chromosome'
        db.delete_table(u'snpdb_chromosome')

        # Deleting model 'Effect'
        db.delete_table(u'snpdb_effect')

        # Deleting model 'Effect_CV'
        db.delete_table(u'snpdb_effect_cv')

        # Deleting model 'Filter'
        db.delete_table(u'snpdb_filter')

        # Deleting model 'Filter_CV'
        db.delete_table(u'snpdb_filter_cv')

        # Deleting model 'SNP'
        db.delete_table(u'snpdb_snp')

        # Deleting model 'SNP_Summary'
        db.delete_table(u'snpdb_snp_summary')

        # Deleting model 'SNP_Type'
        db.delete_table(u'snpdb_snp_type')

        # Deleting model 'Summary_Level_CV'
        db.delete_table(u'snpdb_summary_level_cv')

        # Deleting model 'Statistics_cv'
        db.delete_table(u'snpdb_statistics_cv')

        # Deleting model 'Statistics'
        db.delete_table(u'snpdb_statistics')

        # Deleting model 'SNP_External_DBReference'
        db.delete_table(u'snpdb_snp_external_dbreference')


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
            'protocol': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Protocol']"})
        },
        u'ngsdbview.librarytype': {
            'Meta': {'object_name': 'Librarytype'},
            'librarytype_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '400', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25'})
        },
        u'ngsdbview.lifestage': {
            'Meta': {'object_name': 'Lifestage'},
            'lifestage': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '45'}),
            'lifestage_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '400'})
        },
        u'ngsdbview.organism': {
            'Meta': {'object_name': 'Organism'},
            'genus': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'isolate': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'organism_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organismcode': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
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
            'Meta': {'object_name': 'Protocol'},
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'notes': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '400'}),
            'protocol_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sopfile': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
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
            'effect_class': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'effect_group': ('django.db.models.fields.IntegerField', [], {}),
            'effect_string': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
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