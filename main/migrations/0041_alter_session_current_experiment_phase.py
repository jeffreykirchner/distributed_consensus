# Generated by Django 4.0.8 on 2022-10-28 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0040_remove_sessionplayerpartperiod_earnings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='current_experiment_phase',
            field=models.CharField(choices=[('Instructions', 'Instructions'), ('Run', 'Run'), ('Pay', 'Pay'), ('Done', 'Done')], default='Run', max_length=100),
        ),
    ]
