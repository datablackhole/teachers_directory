# Generated by Django 2.2.22 on 2021-11-11 13:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_delete_userprofile'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Subjects',
        ),
        migrations.DeleteModel(
            name='Teachers',
        ),
    ]
