# Generated by Django 3.2.5 on 2021-07-25 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auto', '0002_auto_20210725_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='detail',
            name='datetime',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
