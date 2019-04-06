from django.conf import settings
from django.db import models
from django.utils import timezone


class Feed(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None)
    alice_passphrase = models.CharField(max_length=200)
    label_string = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    policy_pubkey_hex = models.CharField(max_length=2000, default='Not Created')
    enrico_pubkey_hex = models.CharField(max_length=2000, default='Not Created')
    art_steward_address = models.CharField(max_length=2000, default='0x13a225FB5533bF144F8c484e0E5eD09A6aaDc45c')
    erc721_address = models.CharField(max_length=2000, default='0xe5560289be2a80826ea72dB95e0b14379A7C4d3E')
    provider = models.CharField(max_length=2000, default='http://127.0.0.1:8545')

    """
    def publish(self):
        self.published_date = timezone.now()
        self.save()
    """

    def __str__(self):
        return self.title


class Post(models.Model):
    content = models.CharField(max_length=2000, default='Not Created')
    signature = models.CharField(max_length=2000, default='Not Created')
    enrico_pubkey_hex = models.CharField(max_length=2000, default='Not Created')
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.content
