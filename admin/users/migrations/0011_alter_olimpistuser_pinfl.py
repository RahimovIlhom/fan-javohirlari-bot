# Generated by Django 4.2.11 on 2024-04-18 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_rename_customuser_olimpistuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='olimpistuser',
            name='pinfl',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
