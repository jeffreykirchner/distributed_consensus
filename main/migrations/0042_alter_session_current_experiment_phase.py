# Generated by Django 4.0.8 on 2022-10-28 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0041_alter_session_current_experiment_phase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='current_experiment_phase',
            field=models.CharField(choices=[('Instructions', 'Instructions'), ('Run', 'Run'), ('Pay', 'Pay'), ('Results', 'Results'), ('Done', 'Done')], default='Run', max_length=100),
        ),
    ]
