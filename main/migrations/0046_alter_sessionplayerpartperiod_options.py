# Generated by Django 4.1.2 on 2022-11-01 19:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0045_remove_sessionplayer_current_instruction_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sessionplayerpartperiod',
            options={'ordering': ['session_player_part__session_player', 'parameter_set_labels_period__period_number'], 'verbose_name': 'Session Player Part Period', 'verbose_name_plural': 'Session Player Part Periods'},
        ),
    ]
