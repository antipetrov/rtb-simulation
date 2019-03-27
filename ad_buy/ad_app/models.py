from django.db import models

# Create your models here.


class Ad(models.Model):
    content=models.TextField()
    categories = models.ManyToManyField("Category", related_name="ads")


class Category(models.Model):
    name = models.CharField(verbose_name="Название", max_length=255)
    tag = models.CharField(verbose_name="Тег", max_length=255)
