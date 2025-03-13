from django.db import models


class Credentials(models.Model):
    """
    Model representing credentials with associated metadata for providers
    Stores information such as name, token, URL, priority, and status.
    """
    name = models.CharField(max_length=100)
    token = models.CharField(max_length=100)
    url = models.URLField(max_length=200)
    priority = models.IntegerField(unique=True)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name
