# Generated by Django 2.2.16 on 2023-02-02 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0019_auto_20230202_0921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(help_text='Введите название поста', max_length=150, verbose_name='Заголовок'),
        ),
    ]
