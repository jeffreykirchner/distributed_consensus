# Generated by Django 4.0.8 on 2022-10-19 17:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_remove_session_current_period_session_current_part'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionpart',
            name='current_part_period',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='session_parts_c', to='main.sessionpartperiod'),
        ),
        migrations.AlterField(
            model_name='session',
            name='current_part',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sessions_c', to='main.sessionpart'),
        ),
    ]
