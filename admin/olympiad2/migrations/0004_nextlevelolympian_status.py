# Generated by Django 4.1 on 2024-05-02 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('olympiad2', '0003_nextlevelolympian_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='nextlevelolympian',
            name='status',
            field=models.CharField(default='keladi', max_length=100),
        ),
    ]
