# Generated by Django 2.1.7 on 2019-03-29 17:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0008_feed_enrico_pubkey_hex'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feed',
            old_name='enrico_pubkey_hex',
            new_name='enrico_pubkey',
        ),
    ]
