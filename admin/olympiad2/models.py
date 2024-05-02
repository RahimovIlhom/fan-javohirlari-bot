from django.db import models


class NextLevelOlympian(models.Model):
    tg_id = models.CharField(max_length=30, unique=True)
    fullname = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=30)
    region = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    school_number = models.CharField(max_length=255)
    olympic_science = models.CharField(max_length=30)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    pinfl = models.CharField(max_length=30, null=True, blank=True)
    result = models.DecimalField(max_digits=5, decimal_places=2)
    password = models.CharField(max_length=10, null=True, blank=True)
    status = models.CharField(max_length=100, default="comes")

    class Meta:
        db_table = 'olympians'

    def __str__(self):
        return f"{self.fullname} - {self.olympic_science}"


class OlympicDate(models.Model):
    olympic_science = models.CharField(max_length=30)
    date = models.DateField(null=True, blank=True)
    empty = models.BooleanField(default=True)

    class Meta:
        db_table = 'olympic_dates'


class OlympicTime(models.Model):
    olympic_date = models.ForeignKey(OlympicDate, on_delete=models.SET_NULL, null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    olympians_count = models.IntegerField(default=400)
    empty = models.BooleanField(default=True)

    class Meta:
        db_table = 'olympic_times'
