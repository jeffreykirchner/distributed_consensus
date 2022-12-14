# Generated by Django 4.0.8 on 2022-10-10 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_sessionplayer_name_submitted'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameterset',
            name='part_count',
            field=models.IntegerField(default=3, verbose_name='Number or parts.'),
        ),
        migrations.AlterField(
            model_name='parameterset',
            name='period_count',
            field=models.IntegerField(default=10, verbose_name='Number of periods per part.'),
        ),
    ]
