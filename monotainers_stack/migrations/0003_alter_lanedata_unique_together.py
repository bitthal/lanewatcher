# Generated by Django 4.2 on 2023-05-03 10:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monotainers_stack', '0002_lanedata_lane_lanedata_lower_lanedata_upper_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='lanedata',
            unique_together=set(),
        ),
    ]
