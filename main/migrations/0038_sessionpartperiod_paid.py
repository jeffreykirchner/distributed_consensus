# Generated by Django 4.1.2 on 2022-10-26 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0037_remove_sessionpartperiod_majority_choice'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionpartperiod',
            name='paid',
            field=models.BooleanField(default=False, verbose_name='Pay subjects for this period'),
        ),
    ]
