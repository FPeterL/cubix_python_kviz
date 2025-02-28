import sys, os

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

from django.test import TestCase, Client
from django.urls import reverse
from .models import Question, QuizAttempt
from common_utils import score_string


class ScoreStringTests(TestCase):
    def test_exact_match(self):
        self.assertEqual(score_string("elefánt", "elefánt"), 100)

    def test_transposition_or_small_error(self):
        score = score_string("elefánz", "elefánt")
        self.assertGreater(score, 80)
        self.assertLess(score, 100)

    def test_partial_match(self):
        score = score_string("leonardo de vinchi", "leonardo da vinci")
        self.assertGreater(score, 65)
        self.assertLess(score, 100)

class QuestionModelTests(TestCase):
    def test_question_str(self):
        q = Question.objects.create(text="Melyik a főváros?", times_asked=0, times_correct=0)
        self.assertEqual(str(q), "Melyik a főváros?")

class DashboardViewTests(TestCase):
    def setUp(self):
        Question.objects.create(text="Kérdés 1", times_asked=10, times_correct=7)
        Question.objects.create(text="Kérdés 2", times_asked=5, times_correct=3)
        self.client = Client()

    def test_dashboard_view(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("questions", response.context)
        self.assertIn("users", response.context)

    def test_questions_filtering(self):
        qs = Question.objects.filter(times_asked__gt=0)
        self.assertGreaterEqual(qs.count(), 1)

class QuizAttemptTests(TestCase):
    def setUp(self):
        self.q = Question.objects.create(text="Teszt kérdés", times_asked=0, times_correct=0)
        self.q_attempt_data = {
            "username": "testuser",
            "question": self.q,
            "user_answer": "teszt válasz",
            "correct_option": "A",
            "score": 100
        }

    def test_quiz_attempt_creation(self):
        attempt = QuizAttempt.objects.create(**self.q_attempt_data)
        self.assertEqual(str(attempt), f"{attempt.username} - {attempt.question.text}")
