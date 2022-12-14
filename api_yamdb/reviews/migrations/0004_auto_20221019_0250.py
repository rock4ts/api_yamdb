# Generated by Django 2.2.16 on 2022-10-19 02:50

import django.core.validators
from django.db import migrations, models
import reviews.validators


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_auto_20221018_2323'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
        migrations.AlterField(
            model_name='review',
            name='score',
            field=models.IntegerField(validators=[reviews.validators.score_validator], verbose_name='Оценка'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[django.core.validators.RegexValidator(message=('Username may only consist of letters,', 'digits and @/./+/-/_'), regex='^[\\w.@+-]+$'), reviews.validators.username_validator], verbose_name='Имя пользователя'),
        ),
    ]
