# Generated by Django 2.2.12 on 2020-07-21 16:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pulses',
            name='heart_beat',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='pulses',
            name='time',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
