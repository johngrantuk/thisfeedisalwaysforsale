# Generated by Django 2.1.7 on 2019-03-29 15:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feed',
            name='published_date',
        ),
    ]