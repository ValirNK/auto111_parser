# Generated by Django 3.2.5 on 2021-07-31 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auto', '0007_remove_user_useragent'),
    ]

    operations = [
        migrations.CreateModel(
            name='Result_8',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_1c_part', models.CharField(default='', max_length=36)),
                ('id_1c_doc', models.CharField(default='', max_length=36)),
                ('part_sought', models.CharField(default='', max_length=64)),
                ('brand_sought', models.CharField(default='', max_length=128)),
                ('part_result', models.CharField(default='', max_length=128)),
                ('brand_result', models.CharField(default='', max_length=128)),
                ('title', models.CharField(default='', max_length=128)),
                ('price', models.FloatField()),
                ('day', models.IntegerField()),
                ('qty', models.IntegerField()),
                ('supplier', models.CharField(default='', max_length=64)),
                ('location', models.CharField(default='', max_length=128)),
                ('source', models.CharField(default='', max_length=64)),
                ('datetime', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Деталь',
                'verbose_name_plural': 'Детали',
            },
        ),
        migrations.DeleteModel(
            name='Detail',
        ),
    ]
