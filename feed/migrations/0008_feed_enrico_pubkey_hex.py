# Generated by Django 2.1.7 on 2019-03-29 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0007_auto_20190329_1705'),
    ]

    operations = [
        migrations.AddField(
            model_name='feed',
            name='enrico_pubkey_hex',
            field=models.CharField(default='Not Created', max_length=2000),
        ),
    ]