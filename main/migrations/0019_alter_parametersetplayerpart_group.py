# Generated by Django 4.0.8 on 2022-10-12 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_alter_parametersetlabelsperiod_label'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parametersetplayerpart',
            name='group',
            field=models.IntegerField(default=0, verbose_name='Group Number'),
        ),
    ]
