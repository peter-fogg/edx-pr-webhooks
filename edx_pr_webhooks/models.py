"""
Models for keeping track of users and repos.
"""
from django.db import models


class Repo(models.Model):
    access_token = models.TextField(db_index=True)
    full_name = models.TextField(db_index=True, unique=True)
