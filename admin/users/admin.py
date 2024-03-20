from django.contrib import admin
from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['pinfl', 'fullname', 'phone_number', 'olimpia_science']
    search_fields = ['fullname', 'phone_number']
    list_filter = ['olimpia_science', 'region', 'language']


admin.site.register(CustomUser, CustomUserAdmin)
