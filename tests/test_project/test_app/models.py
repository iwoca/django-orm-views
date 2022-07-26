from django.db import models


class TestModel(models.Model):

    integer_col = models.IntegerField()
    character_col = models.CharField(max_length=100)
    date_col = models.DateField()
    datetime_col = models.DateTimeField()


class TestModelWithForeignKey(models.Model):

    foreign_key = models.ForeignKey(TestModel)
