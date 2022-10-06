# Generated by Django 3.2 on 2021-05-31 17:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_auto_20210531_1724'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliverPayHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('som', models.FloatField()),
                ('dollar', models.FloatField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('deliver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.deliver')),
            ],
            options={
                'verbose_name_plural': '9) Deliver Tolov Tarixi',
            },
        ),
        migrations.CreateModel(
            name='DebtDeliver',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('som', models.FloatField(default=0)),
                ('dollar', models.FloatField(default=0)),
                ('deliver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.deliver')),
            ],
            options={
                'verbose_name_plural': 'Deliver Qarzi',
            },
        ),
    ]