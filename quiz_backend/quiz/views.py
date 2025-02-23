from django.shortcuts import render
from django.db import connection
from .models import Question

def dashboard(request):
    # Csak azok a kérdések, melyeknél legalább egyszer szerepelt a próbálkozás (times_asked > 0)
    questions = Question.objects.filter(times_asked__gt=0)
    question_list = []
    for q in questions:
        times_asked = q.times_asked if q.times_asked is not None else 0
        times_correct = q.times_correct if q.times_correct is not None else 0
        times_incorrect = times_asked - times_correct

        if times_asked:
            success_rate = round(times_correct / times_asked * 100, 2)
        else:
            success_rate = 0
        question_list.append({
            'text': q.text,
            'times_asked': times_asked,
            'times_correct': times_correct,
            'times_incorrect': times_incorrect,
            'success_rate': success_rate,
        })

    # Felhasználói eredmények lekérdezése a quiz_attempt táblából
    user_stats = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT username, COUNT(*) as total,
                SUM(CASE WHEN score = 100 THEN 1 ELSE 0 END) as correct
            FROM quiz_attempt
            GROUP BY username
            ORDER BY (SUM(CASE WHEN score = 100 THEN 1 ELSE 0 END) * 1.0 / COUNT(*)) DESC
        """)
        rows = cursor.fetchall()
        for row in rows:
            username, total, correct = row
            correct = correct if correct is not None else 0
            incorrect = total - correct
            if total > 0:
                performance_percentage = round((correct * 100.0) / total, 2)
            else:
                performance_percentage = 0
            user_stats.append({
                'username': username,
                'total': total,
                'correct': correct,
                'incorrect': incorrect,
                'performance_percentage': performance_percentage
            })

    context = {
        'questions': question_list,
        'users': user_stats,
    }
    return render(request, 'dashboard.html', context)
