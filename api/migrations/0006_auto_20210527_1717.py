# Generated by Django 3.2 on 2021-05-27 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20210525_1233'),
    ]

    operations = [
        migrations.AddField(
            model_name='debtor',
            name='debts_dollar',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='payhistory',
            name='dollar',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='returnproduct',
            name='dollar',
            field=models.FloatField(default=0),
        ),
    ]
