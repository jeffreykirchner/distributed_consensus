# Generated by Django 4.1.2 on 2022-11-04 18:47

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0047_alter_parameterset_period_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionplayer',
            name='result',
            field=models.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True),
        ),
    ]
