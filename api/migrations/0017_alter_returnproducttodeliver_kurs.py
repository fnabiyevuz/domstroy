# Generated by Django 3.2 on 2021-06-01 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_auto_20210601_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='returnproducttodeliver',
            name='kurs',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
