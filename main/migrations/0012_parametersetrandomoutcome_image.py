# Generated by Django 4.0.8 on 2022-10-11 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_alter_parameterset_period_length_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='parametersetrandomoutcome',
            name='image',
            field=models.CharField(default='abc.jpg', max_length=100),
        ),
    ]
