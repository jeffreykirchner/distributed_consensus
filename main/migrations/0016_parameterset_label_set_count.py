# Generated by Django 4.0.8 on 2022-10-12 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_alter_parametersetlabelsperiod_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameterset',
            name='label_set_count',
            field=models.IntegerField(default=3, verbose_name='Number or label sets.'),
        ),
    ]