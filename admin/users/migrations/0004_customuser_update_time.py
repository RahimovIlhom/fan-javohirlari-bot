# Generated by Django 5.0.1 on 2024-02-01 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_customuser_created_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='update_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
