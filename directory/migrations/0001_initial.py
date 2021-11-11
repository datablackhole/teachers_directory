# Generated by Django 2.2.22 on 2021-11-11 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Subjects',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject_name', models.CharField(max_length=240)),
            ],
        ),
        migrations.CreateModel(
            name='Teachers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=240)),
                ('last_name', models.CharField(max_length=240)),
                ('profile_picture', models.ImageField(upload_to='')),
                ('email_address', models.CharField(max_length=240)),
                ('phone_number', models.CharField(max_length=240)),
                ('room_number', models.CharField(max_length=240)),
                ('subjects_taught', models.CharField(max_length=240)),
            ],
        ),
    ]