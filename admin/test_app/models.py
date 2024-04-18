from django.db import models


languages = (
    ('uzbek', 'uzbek'),
    ('russian', 'russian')
)


class Test(models.Model):
    science = models.CharField(max_length=20)
    create_time = models.DateField(auto_now_add=True)
    language = models.CharField(max_length=7, choices=languages, default=languages[0])
    questions_count = models.IntegerField(default=10)
    is_confirm = models.BooleanField(default=False)
    olympiad_test = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tests'

    def __str__(self):
        return f"{self.science} {self.create_time} - {self.language} testi"


class TestQuestion(models.Model):
    number_question = models.IntegerField(null=True)
    question_uz = models.TextField(null=True, blank=True)
    question_ru = models.TextField(null=True, blank=True)
    true_response = models.IntegerField()
    test = models.ForeignKey(Test, related_name='test_questions', on_delete=models.SET_NULL, null=True)
    image_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'test_questions'

    def __str__(self):
        test_str = self.test.__str__()
        return f"{test_str}, {self.number_question}-savol"


class TestResult(models.Model):
    tg_id = models.CharField(max_length=20)
    language = models.CharField(max_length=10)
    fullname = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=30)
    region = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    school_number = models.CharField(max_length=255)
    science = models.CharField(max_length=20)
    responses = models.CharField(max_length=50)
    result_time = models.DateTimeField(auto_now_add=True)
    test = models.ForeignKey(Test, on_delete=models.SET_NULL, null=True, blank=True)
    pinfl = models.CharField(max_length=30, null=True, blank=True)
    certificate_image = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'test_result'

    def __str__(self):
        return f"{self.fullname} - {self.science} - {self.result_time}"
