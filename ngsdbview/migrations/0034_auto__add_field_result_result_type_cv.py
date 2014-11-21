# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Result.result_type_cv'
        db.add_column(u'ngsdbview_result', 'result_type_cv',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['ngsdbview.Result_CV']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Result.result_type_cv'
        db.delete_column(u'ngsdbview_result', 'result_type_cv_id')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'ngsdbview.analysis': {
            'Meta': {'object_name': 'Analysis'},
            'analysis_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'analysistype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Analysistype']"}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Result']"}),
            'software': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Software']"}),
            'time_data_loaded': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'ngsdbview.analysiscv': {
            'Meta': {'object_name': 'AnalysisCV'},
            'analysis_cv_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'cvterm': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'dbxref': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Dbxref']"}),
            'definition': ('django.db.models.fields.TextField', [], {}),
            'is_obsolete': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_relationshiptype': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'ngsdbview.analysisfile': {
            'Meta': {'object_name': 'Analysisfile'},
            'analysis': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Analysis']"}),
            'analysisfile_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'notes': ('django.db.models.fields.CharField', [], {'default': "'analysis'", 'max_length': '1000'})
        },
        u'ngsdbview.analysisprop': {
            'Meta': {'object_name': 'Analysisprop'},
            'analysis': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Analysis']"}),
            'analysisprop_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'cvterm': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Cvterm']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        u'ngsdbview.analysistype': {
            'Meta': {'object_name': 'Analysistype'},
            'analysistype_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'definition': ('django.db.models.fields.TextField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
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
        u'ngsdbview.cv': {
            'Meta': {'object_name': 'Cv'},
            'cv_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'definition': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'})
        },
        u'ngsdbview.cvterm': {
            'Meta': {'object_name': 'Cvterm'},
            'cv': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Cv']"}),
            'cvterm_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'dbxref': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Dbxref']"}),
            'definition': ('django.db.models.fields.TextField', [], {}),
            'is_obsolete': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_relationshiptype': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'db_index': 'True'})
        },
        u'ngsdbview.dbxref': {
            'Meta': {'object_name': 'Dbxref'},
            'dbxref_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'definition': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'ngsdbview.experiment': {
            'Meta': {'object_name': 'Experiment'},
            'author_modified': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'experiment_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'libraries': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['samples.Library']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_index': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        u'ngsdbview.feature': {
            'Meta': {'object_name': 'Feature'},
            'aa_seq': ('django.db.models.fields.TextField', [], {}),
            'annotation': ('django.db.models.fields.CharField', [], {'max_length': '500', 'db_index': 'True'}),
            'chromosome': ('django.db.models.fields.CharField', [], {'max_length': '45', 'db_index': 'True'}),
            'feature_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'featuretype': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'fmax': ('django.db.models.fields.IntegerField', [], {}),
            'fmin': ('django.db.models.fields.IntegerField', [], {}),
            'geneid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'geneproduct': ('django.db.models.fields.CharField', [], {'max_length': '500', 'db_index': 'True'}),
            'genome': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Genome']"}),
            'na_seq': ('django.db.models.fields.TextField', [], {}),
            'phase': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'strand': ('django.db.models.fields.IntegerField', [], {}),
            'time_data_loaded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'time_data_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'ngsdbview.geneidmap': {
            'Meta': {'object_name': 'Geneidmap'},
            'db_soruce_current': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'db_soruce_previous': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'db_version_current': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'db_version_previous': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'geneid_current': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'geneid_previous': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'geneidmap_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_data_loaded': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
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
        u'ngsdbview.genotype': {
            'Meta': {'ordering': "['genotype']", 'object_name': 'Genotype'},
            'genotype': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '45'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '45', 'blank': 'True'})
        },
        u'ngsdbview.growthphase': {
            'Meta': {'ordering': "['growthphase']", 'object_name': 'Growthphase'},
            'growthphase': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '400', 'blank': 'True'})
        },
        u'ngsdbview.library_cv': {
            'Meta': {'object_name': 'Library_CV'},
            'cvterm': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'dbxref': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Dbxref']"}),
            'definition': ('django.db.models.fields.TextField', [], {}),
            'is_obsolete': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_relationshiptype': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'library_cv_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'ngsdbview.libraryfile': {
            'Meta': {'object_name': 'Libraryfile'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'library': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['samples.Library']"}),
            'libraryfile_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.CharField', [], {'default': "'qc'", 'max_length': '1000'})
        },
        u'ngsdbview.libraryprop': {
            'Meta': {'object_name': 'Libraryprop'},
            'cvterm': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Cvterm']"}),
            'library': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['samples.Library']"}),
            'libraryprop_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {})
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
            'libraries': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['samples.Library']", 'symmetrical': 'False'}),
            'notes': ('django.db.models.fields.TextField', [], {'default': 'None'}),
            'result_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'result_type_cv': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Result_CV']"}),
            'time_data_loaded': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'ngsdbview.result_cv': {
            'Meta': {'object_name': 'Result_CV'},
            'cvterm': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'dbxref': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Dbxref']"}),
            'definition': ('django.db.models.fields.TextField', [], {}),
            'is_obsolete': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_relationshiptype': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'result_cv_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'ngsdbview.resultfile': {
            'Meta': {'object_name': 'Resultfile'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'notes': ('django.db.models.fields.CharField', [], {'default': "'result'", 'max_length': '1000'}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Result']"}),
            'resultfile_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'ngsdbview.resultprop': {
            'Meta': {'object_name': 'Resultprop'},
            'cvterm': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Cvterm']"}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Result']"}),
            'resultprop_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        u'ngsdbview.resultraw': {
            'Meta': {'object_name': 'Resultraw'},
            'chromosome': ('django.db.models.fields.CharField', [], {'max_length': '250', 'db_index': 'True'}),
            'majorstrand': ('django.db.models.fields.IntegerField', [], {}),
            'negstrandcount': ('django.db.models.fields.IntegerField', [], {}),
            'position': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'posstrandcount': ('django.db.models.fields.IntegerField', [], {}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Result']"}),
            'resultraw_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_data_loaded': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'totalcount': ('django.db.models.fields.IntegerField', [], {})
        },
        u'ngsdbview.resultslgene': {
            'Meta': {'object_name': 'Resultslgene'},
            'antisensereadcount': ('django.db.models.fields.IntegerField', [], {}),
            'antisensesitecount': ('django.db.models.fields.IntegerField', [], {}),
            'cdsend': ('django.db.models.fields.IntegerField', [], {}),
            'cdsstart': ('django.db.models.fields.IntegerField', [], {}),
            'chromosome': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'geneid': ('django.db.models.fields.CharField', [], {'max_length': '45', 'db_index': 'True'}),
            'genestrand': ('django.db.models.fields.IntegerField', [], {}),
            'putative5utr': ('django.db.models.fields.IntegerField', [], {}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Result']"}),
            'resultslgene_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sensedownsitecount': ('django.db.models.fields.IntegerField', [], {}),
            'sensereadcount': ('django.db.models.fields.IntegerField', [], {}),
            'sensesitecount': ('django.db.models.fields.IntegerField', [], {}),
            'senseupsitecount': ('django.db.models.fields.IntegerField', [], {}),
            'time_data_loaded': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'ngsdbview.resultslsite': {
            'Meta': {'object_name': 'Resultslsite'},
            'cdsend': ('django.db.models.fields.IntegerField', [], {}),
            'cdsstart': ('django.db.models.fields.IntegerField', [], {}),
            'chromosome': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'geneid': ('django.db.models.fields.CharField', [], {'max_length': '45', 'db_index': 'True'}),
            'genestrand': ('django.db.models.fields.IntegerField', [], {}),
            'intervallength': ('django.db.models.fields.IntegerField', [], {}),
            'position': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'putative5utr': ('django.db.models.fields.IntegerField', [], {}),
            'rank': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'readcount': ('django.db.models.fields.IntegerField', [], {}),
            'readstrand': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Result']"}),
            'resultslsite_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slid': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'slpercent': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '7'}),
            'time_data_loaded': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'ngsdbview.resultsriboprof': {
            'Meta': {'object_name': 'Resultsriboprof'},
            'counts_normalized': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '4'}),
            'counts_raw': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '4'}),
            'featuretype': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            'geneid': ('django.db.models.fields.CharField', [], {'max_length': '45', 'db_index': 'True'}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Result']"}),
            'resultsriboprof_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_data_loaded': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'ngsdbview.seqtech': {
            'Meta': {'object_name': 'Seqtech'},
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'seqtech_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'ngsdbview.software': {
            'Meta': {'object_name': 'Software'},
            'algorithm': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'notes': ('django.db.models.fields.TextField', [], {'default': 'None'}),
            'software_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sourceuri': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'ngsdbview.templibraryprop': {
            'Meta': {'object_name': 'Templibraryprop'},
            'cvterm_id': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library_id': ('django.db.models.fields.IntegerField', [], {}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        u'ngsdbview.tempmtom': {
            'Meta': {'object_name': 'Tempmtom'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ngsdbview_libcode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            'ngsdbview_libid': ('django.db.models.fields.IntegerField', [], {}),
            'result_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'db_index': 'True'}),
            'samples_libid': ('django.db.models.fields.IntegerField', [], {})
        },
        u'ngsdbview.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'libraries': ('django.db.models.fields.related.ManyToManyField', [], {'default': "['AH006']", 'to': u"orm['samples.Library']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'samples.bioproject': {
            'Meta': {'object_name': 'Bioproject'},
            'bioproject_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '400', 'blank': 'True'}),
            'organisms': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'sharepoint_projectcode': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'})
        },
        u'samples.biosample': {
            'Meta': {'object_name': 'Biosample'},
            'biosample_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12'}),
            'collected_on_test': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '400', 'blank': 'True'}),
            'organisms': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'samples.library': {
            'Meta': {'object_name': 'Library'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ngsdbview.authors'", 'to': u"orm['ngsdbview.Author']"}),
            'author_modified': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'bioproject': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['samples.Bioproject']"}),
            'collaborator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ngsdbview.collaborator'", 'to': u"orm['ngsdbview.Collaborator']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'experiment_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'fastqfile_md5sum': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'fastqfile_name': ('django.db.models.fields.CharField', [], {'max_length': '254', 'null': 'True', 'blank': 'True'}),
            'fastqfile_readcount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '25', 'decimal_places': '2', 'blank': 'True'}),
            'fastqfile_size_inbytes': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '50', 'decimal_places': '2', 'blank': 'True'}),
            'flowcell_number': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index_sequence': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'lane_number': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'library_code': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '10', 'blank': 'True'}),
            'library_creation_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'library_gelimage': ('django.db.models.fields.files.FileField', [], {'default': "'NA'", 'max_length': '100', 'blank': 'True'}),
            'librarytype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ngsdbview.librarytype'", 'to': u"orm['ngsdbview.Librarytype']"}),
            'note_for_analysis': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'protocol': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ngsdbview.protocol'", 'to': u"orm['ngsdbview.Protocol']"}),
            'protocol_notes': ('django.db.models.fields.TextField', [], {'default': "'None'", 'blank': 'True'}),
            'sampleid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['samples.Sample']", 'null': 'True'}),
            'sequence_downloaded_on': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'submitted_for_sequencing_on': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'suggested_reference_genome': ('django.db.models.fields.CharField', [], {'default': "'Genome: xxxxx ; Version: xxxx'", 'max_length': '100', 'blank': 'True'}),
            'template_material': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'samples.sample': {
            'Meta': {'object_name': 'Sample'},
            'author_modified': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'bioanalyzer_analysis': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'biological_replicate_of': ('django.db.models.fields.CharField', [], {'default': "'No Replicate'", 'max_length': '25', 'blank': 'True'}),
            'biosample': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['samples.Biosample']"}),
            'collaborator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ngsdbview.collaboratorS'", 'to': u"orm['ngsdbview.Collaborator']"}),
            'collected_at': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'collected_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'collected_by_emailid': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'blank': 'True'}),
            'collected_on': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'culture_method': ('django.db.models.fields.CharField', [], {'default': "'axenic-culture'", 'max_length': '100'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'date_received': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'freezer_location': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'genotype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ngsdbview.genotypeS'", 'to': u"orm['ngsdbview.Genotype']"}),
            'growthphase': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ngsdbview.growthphaseS'", 'to': u"orm['ngsdbview.Growthphase']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_clonal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'isolation_method': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'label_ontube': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '250', 'blank': 'True'}),
            'lifestage': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ngsdbview.lifestageS'", 'to': u"orm['ngsdbview.Lifestage']"}),
            'organism': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sample_organism'", 'to': u"orm['ngsdbview.Organism']"}),
            'parent_sampleid': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '25', 'blank': 'True'}),
            'phenotype': ('django.db.models.fields.CharField', [], {'default': "'wildtype'", 'max_length': '254'}),
            'sample_concentration': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '4', 'blank': 'True'}),
            'sample_dilution': ('django.db.models.fields.CharField', [], {'default': "'Original Concentration'", 'max_length': '25', 'blank': 'True'}),
            'sample_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'sample_quantity': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '4', 'blank': 'True'}),
            'sample_volume': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'sampleid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25', 'db_index': 'True'}),
            'sampletype': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sourcename': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['samples.Source']"}),
            'time_after_treatment': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'treatment': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'samples.source': {
            'Meta': {'object_name': 'Source'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['ngsdbview']