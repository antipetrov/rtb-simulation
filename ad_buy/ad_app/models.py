from django.db import models

# Create your models here.


class Ad(models.Model):

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'

    content = models.TextField()
    categories = models.ManyToManyField("Category", related_name="ads", verbose_name="Категории", )

    def __str__(self):
        return "Объявление #{}: {}".format(self.pk, self.content[:32])


class Category(models.Model):

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    name = models.CharField(verbose_name="Название", max_length=255)
    tag = models.CharField(verbose_name="Тег", max_length=255)

    def __str__(self):
        return "Категория #{}: {}".format(self.pk, self.name)