# Generated by Django 3.0.6 on 2020-05-30 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Shop', '0002_auto_20200530_2331'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sub_catgory',
            field=models.CharField(default='', max_length=20),
        ),
    ]
