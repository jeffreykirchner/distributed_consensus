# Generated by Django 4.0.8 on 2022-10-24 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_rename_current_part_session_current_session_part'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionpart',
            name='results_shown',
            field=models.BooleanField(default=False, verbose_name='Results Shown'),
        ),
    ]
