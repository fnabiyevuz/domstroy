# Generated by Django 3.2 on 2021-05-19 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_returnproducttodeliver_kurs'),
    ]

    operations = [
        migrations.AddField(
            model_name='fakturaitem',
            name='body_dollar',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='fakturaitem',
            name='body_som',
            field=models.FloatField(default=0),
        ),
    ]
