from django.contrib import admin
from .models import OlimpistUser, Token


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['pinfl', 'fullname', 'phone_number', 'olimpia_science']
    search_fields = ['fullname', 'phone_number']
    list_filter = ['olimpia_science', 'region', 'language']


admin.site.register(OlimpistUser, CustomUserAdmin)
admin.site.register(Token)
