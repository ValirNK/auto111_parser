# Generated by Django 3.2.5 on 2021-07-25 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auto', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='detail',
            name='name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='detail',
            name='sku',
            field=models.CharField(default='', max_length=50),
        ),
    ]
