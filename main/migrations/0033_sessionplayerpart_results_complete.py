# Generated by Django 4.0.8 on 2022-10-24 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_sessionpart_results_shown'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionplayerpart',
            name='results_complete',
            field=models.BooleanField(default=False, verbose_name='Results Complete'),
        ),
    ]
