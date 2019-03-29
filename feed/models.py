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
    policy_pubkey = models.CharField(max_length=2000, default='Not Created')

    """
    def publish(self):
        self.published_date = timezone.now()
        self.save()
    """

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title + ": " + self.content
