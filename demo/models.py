from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=50)
    body = models.TextField()

class Page(models.Model):
    title = models.CharField(max_length=50)
    body = models.TextField()
