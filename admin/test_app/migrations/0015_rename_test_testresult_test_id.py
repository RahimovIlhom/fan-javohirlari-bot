# Generated by Django 4.1 on 2024-04-19 17:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('test_app', '0014_alter_testresult_test'),
    ]

    operations = [
        migrations.RenameField(
            model_name='testresult',
            old_name='test',
            new_name='test_id',
        ),
    ]