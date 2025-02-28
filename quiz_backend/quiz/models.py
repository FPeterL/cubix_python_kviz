from django.db import models

class Question(models.Model):
    QUESTION_TYPES = [
        ('MC', 'Multiple Choice'),
        ('DATE', 'Date Input'),
        ('STRING', 'String Matching'),
    ]
    text = models.CharField("Kérdés", max_length=500)
    question_type = models.CharField("Kérdés típusa", max_length=10, choices=QUESTION_TYPES, default='MC')
    # Multiple choice opciók – csak MC típus esetén használatos
    option_a = models.CharField("Válasz A", max_length=200, blank=True, null=True)
    option_b = models.CharField("Válasz B", max_length=200, blank=True, null=True)
    option_c = models.CharField("Válasz C", max_length=200, blank=True, null=True)
    option_d = models.CharField("Válasz D", max_length=200, blank=True, null=True)
    correct_option = models.CharField(
        "Helyes válasz (MC)",
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
        blank=True,
        null=True
    )
    # DATE/STRING típusú kérdés esetén a helyes válasz szövege
    correct_answer = models.CharField("Helyes válasz (szöveg)", max_length=200, blank=True, null=True)
    times_asked = models.IntegerField("Futtatások száma", default=0)
    times_correct = models.IntegerField("Helyes válaszok száma", default=0)

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    username = models.CharField("Felhasználó", max_length=200)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Kérdés")
    user_answer = models.CharField("Felhasználó válasza", max_length=200)
    correct_option = models.CharField("Helyes válasz", max_length=200, blank=True, null=True)
    score = models.FloatField("Pontszám", default=0)
    timestamp = models.DateTimeField("Időbélyeg", auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.question.text}"

    class Meta:
        db_table = "quiz_attempt"
