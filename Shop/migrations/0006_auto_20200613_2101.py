# Generated by Django 3.0.6 on 2020-06-13 15:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Shop', '0005_orders'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Orders',
            new_name='Order',
        ),
    ]
