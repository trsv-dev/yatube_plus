# Generated by Django 3.2.15 on 2023-02-09 11:47

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0025_auto_20230205_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='like',
            name='value',
            field=models.CharField(choices=[('Нравится', 'Нравится'), ('Не нравится', 'Не нравится')], default='Нравится', max_length=11, verbose_name='Значение'),
        ),
        migrations.AlterField(
            model_name='post',
            name='liked',
            field=models.ManyToManyField(blank=True, default=None, related_name='Лайкнули', to=settings.AUTH_USER_MODEL),
        ),
    ]
