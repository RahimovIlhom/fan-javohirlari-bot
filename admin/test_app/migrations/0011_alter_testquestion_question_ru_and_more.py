# Generated by Django 4.2.11 on 2024-04-18 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test_app', '0010_remove_testquestion_test_testquestion_test'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testquestion',
            name='question_ru',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testquestion',
            name='question_uz',
            field=models.TextField(blank=True, null=True),
        ),
    ]