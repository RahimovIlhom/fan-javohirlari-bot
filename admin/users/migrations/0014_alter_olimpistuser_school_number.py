# Generated by Django 4.2.11 on 2024-04-18 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_alter_olimpistuser_school_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='olimpistuser',
            name='school_number',
            field=models.CharField(max_length=100),
        ),
    ]