# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'CNV_CV', fields ['cvterm']
        db.create_index(u'snpdb_cnv_cv', ['cvterm'])

        # Adding index on 'CNV_CV', fields ['cv_value']
        db.create_index(u'snpdb_cnv_cv', ['cv_value'])

        # Adding index on 'SNP_CV', fields ['cvterm']
        db.create_index(u'snpdb_snp_cv', ['cvterm'])

        # Adding index on 'SNP_CV', fields ['cv_value']
        db.create_index(u'snpdb_snp_cv', ['cv_value'])

        # Adding index on 'Statistics_cv', fields ['cvterm']
        db.create_index(u'snpdb_statistics_cv', ['cvterm'])

        # Adding index on 'Filter_CV', fields ['filter_type']
        db.create_index(u'snpdb_filter_cv', ['filter_type'])


    def backwards(self, orm):
        # Removing index on 'Filter_CV', fields ['filter_type']
        db.delete_index(u'snpdb_filter_cv', ['filter_type'])

        # Removing index on 'Statistics_cv', fields ['cvterm']
        db.delete_index(u'snpdb_statistics_cv', ['cvterm'])

        # Removing index on 'SNP_CV', fields ['cv_value']
        db.delete_index(u'snpdb_snp_cv', ['cv_value'])

        # Removing index on 'SNP_CV', fields ['cvterm']
        db.delete_index(u'snpdb_snp_cv', ['cvterm'])

        # Removing index on 'CNV_CV', fields ['cv_value']
        db.delete_index(u'snpdb_cnv_cv', ['cv_value'])

        # Removing index on 'CNV_CV', fields ['cvterm']
        db.delete_index(u'snpdb_cnv_cv', ['cvterm'])


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
            'time_data_loaded': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
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
        },
        u'snpdb.chromosome': {
            'Meta': {'object_name': 'Chromosome'},
            'chromosome_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'chromosome_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'genome_name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Organism']", 'to_field': "'organismcode'"}),
            'genome_version': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'size': ('django.db.models.fields.IntegerField', [], {})
        },
        u'snpdb.cnv': {
            'CNV_value': ('django.db.models.fields.IntegerField', [], {}),
            'Meta': {'object_name': 'CNV'},
            'chromosome': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.Chromosome']"}),
            'cnv_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['samples.Library']"}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Result']"}),
            'start': ('django.db.models.fields.IntegerField', [], {}),
            'stop': ('django.db.models.fields.IntegerField', [], {}),
            'window_size': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.CNV_CV']"})
        },
        u'snpdb.cnv_cv': {
            'Meta': {'object_name': 'CNV_CV'},
            'cv_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'cv_value': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'cvterm': ('django.db.models.fields.TextField', [], {'db_index': 'True'})
        },
        u'snpdb.effect': {
            'Meta': {'object_name': 'Effect'},
            'effect': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.Effect_CV']"}),
            'effect_class': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'effect_group': ('django.db.models.fields.IntegerField', [], {}),
            'effect_string': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'snp': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.SNP']"})
        },
        u'snpdb.effect_cv': {
            'Meta': {'object_name': 'Effect_CV'},
            'effect_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'effect_name': ('django.db.models.fields.CharField', [], {'max_length': '45', 'db_index': 'True'})
        },
        u'snpdb.filter': {
            'Meta': {'object_name': 'Filter'},
            'filter_cv': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.Filter_CV']"}),
            'filter_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'filter_result': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'snp': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.SNP']"})
        },
        u'snpdb.filter_cv': {
            'Meta': {'object_name': 'Filter_CV'},
            'filter_cv_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'filter_type': ('django.db.models.fields.TextField', [], {'db_index': 'True'})
        },
        u'snpdb.snp': {
            'Meta': {'object_name': 'SNP'},
            'alt_base': ('django.db.models.fields.TextField', [], {}),
            'chromosome': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.Chromosome']"}),
            'heterozygosity': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'library': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['samples.Library']"}),
            'quality': ('django.db.models.fields.IntegerField', [], {}),
            'ref_base': ('django.db.models.fields.TextField', [], {}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Result']"}),
            'snp_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'snp_position': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'vcf': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.VCF_Files']"})
        },
        u'snpdb.snp_cv': {
            'Meta': {'object_name': 'SNP_CV'},
            'cv_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'cv_value': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'cvterm': ('django.db.models.fields.TextField', [], {'db_index': 'True'})
        },
        u'snpdb.snp_external_dbreference': {
            'Meta': {'object_name': 'SNP_External_DBReference'},
            'databaseReference_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'db_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'snp': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.SNP']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'snpdb.snp_type': {
            'Meta': {'object_name': 'SNP_Type'},
            'deletion': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'indel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_snp': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'monomorphic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'snp': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['snpdb.SNP']"}),
            'snptype_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sv': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'transition': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
            'cvterm': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'stats_cvterm_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'snpdb.vcf_files': {
            'Meta': {'object_name': 'VCF_Files'},
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'date_uploaded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'library': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['samples.Library']"}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ngsdbview.Result']"}),
            'vcf_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'vcf_md5sum': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'vcf_path': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['snpdb']