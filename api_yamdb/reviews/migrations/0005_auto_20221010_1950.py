# Generated by Django 2.2.16 on 2022-10-10 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_auto_20221010_1948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.IntegerField(default=2022, verbose_name='Год публикации'),
        ),
    ]
