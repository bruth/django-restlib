from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=20)


class Library(models.Model):
    name = models.CharField(max_length=30)
    url = models.URLField()
    language = models.CharField(max_length=20)
    tags = models.ManyToManyField(Tag)


class Hacker(models.Model):
    name = models.CharField(max_length=30)
    website = models.URLField()
    libraries = models.ManyToManyField(Library)
    tags = models.ManyToManyField(Tag)


class Book(models.Model):
    title = models.CharField(max_length=50)
    author = models.ForeignKey(Hacker)
    pub_date = models.DateField(null=True)
    tags = models.ManyToManyField(Tag)

