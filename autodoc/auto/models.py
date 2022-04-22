from django.db import models

class Result_8(models.Model):
    id_1c_part = models.CharField(max_length=36, default='')
    id_1c_doc = models.CharField(max_length=36, default='')
    part_sought = models.CharField(max_length=64, default='')
    brand_sought = models.CharField(max_length=128, default='')
    part_result = models.CharField(max_length=128, default='')
    brand_result = models.CharField(max_length=128, default='')
    title = models.CharField(max_length=128, default='')
    price = models.FloatField()
    day = models.IntegerField()
    qty = models.IntegerField()
    supplier = models.CharField(max_length=64, default='')
    location = models.CharField(max_length=128, default='')
    source = models.CharField(max_length=64, default='')
    datetime = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ["horn_length"]
        verbose_name = "Деталь"
        verbose_name_plural = "Детали"

    def __str__(self):
        return self.title


class Needs_8(models.Model):
    id_1c_part = models.CharField(max_length=38, default='')
    id_1c_doc = models.CharField(max_length=38, default='')
    part_sought = models.CharField(max_length=255, default='')
    brand_sought = models.CharField(max_length=255, default='')
    status = models.IntegerField()

    class Meta:
        # ordering = ["horn_length"]
        verbose_name = "needs_8"

    def __str__(self):
        return self.part_sought

class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    proxy = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username