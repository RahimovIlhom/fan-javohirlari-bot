# Generated by Django 5.0.1 on 2024-01-31 23:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_customuser_created_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='created_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
