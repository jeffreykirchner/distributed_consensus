# Generated by Django 4.0.8 on 2022-10-24 21:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0033_sessionplayerpart_results_complete'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sessionpart',
            old_name='results_shown',
            new_name='show_results',
        ),
    ]
