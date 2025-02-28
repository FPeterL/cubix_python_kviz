from django.contrib import admin
from .models import Question, QuizAttempt

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question_type', 'times_asked', 'times_correct')

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('username', 'question', 'user_answer', 'correct_option', 'score', 'timestamp')
    list_filter = ('username', 'timestamp')
    search_fields = ('username', 'question__text')
