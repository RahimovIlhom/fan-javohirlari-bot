from django.db import models


class CustomUser(models.Model):
    tg_id = models.CharField(max_length=20, unique=True)
    language = models.CharField(max_length=10)
    fullname = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    region = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    school_number = models.CharField(max_length=20)
    science_1 = models.CharField(max_length=20, null=True, blank=True)
    science_2 = models.CharField(max_length=20, null=True, blank=True)
    science_3 = models.CharField(max_length=20, null=True, blank=True)
    olimpia_science = models.CharField(max_length=20)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fullname} - {self.phone_number}"

    class Meta:
        db_table = 'users'
