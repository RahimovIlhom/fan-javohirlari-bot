# Generated by Django 4.1 on 2024-04-29 15:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('olympiad2', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OlympicTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.TimeField(blank=True, null=True)),
                ('olympians_count', models.IntegerField(default=400)),
                ('empty', models.BooleanField(default=True)),
                ('olympic_date', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='olympiad2.olympicdate')),
            ],
            options={
                'db_table': 'olympic_times',
            },
        ),
    ]
