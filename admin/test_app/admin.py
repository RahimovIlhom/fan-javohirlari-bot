from django.contrib import admin
from .models import Test, TestQuestion, TestResult


admin.site.register(Test)
admin.site.register(TestQuestion)
admin.site.register(TestResult)
