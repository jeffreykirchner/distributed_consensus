# Generated by Django 4.0.8 on 2022-10-10 18:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_parametersetpart_parametersetpartperiod'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParameterSetLabels',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Name Here', max_length=1000)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('parameter_set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set_labels', to='main.parameterset')),
            ],
            options={
                'verbose_name': 'Parameter Set Labels',
                'verbose_name_plural': 'Parameter Set Labels',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ParameterSetRandomOutcome',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Name Here', max_length=100)),
                ('abbreviation', models.CharField(default='Abbreviation Here', max_length=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('parameter_set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set_random_outcomes', to='main.parameterset')),
            ],
            options={
                'verbose_name': 'Parameter Set Random Outcome',
                'verbose_name_plural': 'Parameter Set Random Outcomes',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ParameterSetLabelsPeriod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period_number', models.IntegerField(default=0, verbose_name='Period Number')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('label', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set_labels_periods_b', to='main.parametersetrandomoutcome')),
                ('parameter_set_labels', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameter_set_labels_periods_a', to='main.parametersetlabels')),
            ],
            options={
                'verbose_name': 'Parameter Set Labels Period',
                'verbose_name_plural': 'Parameter Set Labels Period',
                'ordering': ['period_number'],
            },
        ),
    ]