from django.contrib import admin
from .models import Test, TestQuestion, TestResult


class TestAdmin(admin.ModelAdmin):
    list_display = ['id', 'science', 'language', 'questions_count', 'is_confirm']


admin.site.register(Test, TestAdmin)
admin.site.register(TestQuestion)
admin.site.register(TestResult)
