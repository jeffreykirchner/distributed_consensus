# Generated by Django 4.1.2 on 2022-11-17 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0056_parametersetrandomoutcome_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionplayerpartperiod',
            name='choice_length',
            field=models.IntegerField(default=0, verbose_name='Choice Length'),
        ),
    ]
