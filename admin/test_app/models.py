from django.db import models


class Test(models.Model):
    science = models.CharField(max_length=20)
    create_time = models.DateField(auto_now_add=True)
    time_continue = models.IntegerField(default=120)
    questions_count = models.IntegerField(default=10)
    is_confirm = models.BooleanField(default=False)

    class Meta:
        db_table = 'tests'

    def __str__(self):
        return f"{self.science} {self.create_time} testi"


class TestQuestion(models.Model):
    number_question = models.IntegerField(null=True)
    question_uz = models.CharField(max_length=500)
    question_ru = models.CharField(max_length=500)
    true_response = models.IntegerField()
    test = models.ManyToManyField(Test, related_name='test_questions')

    class Meta:
        db_table = 'test_questions'

    def __str__(self):
        test_str = str(self.test.first()) if self.test.exists() else "No Test"
        return f"{test_str}, {self.number_question}-savol"


class TestResult(models.Model):
    tg_id = models.CharField(max_length=20)
    language = models.CharField(max_length=10)
    fullname = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    region = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    school_number = models.CharField(max_length=20)
    science = models.CharField(max_length=20)
    responses = models.CharField(max_length=50)
    result_time = models.DateTimeField(auto_now_add=True)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)

    class Meta:
        db_table = 'test_result'

    def __str__(self):
        return f"{self.fullname} - {self.science} - {self.result_time}"
