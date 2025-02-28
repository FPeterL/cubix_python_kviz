import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quiz_backend.settings')
django.setup()

from quiz.models import Question, QuizAttempt

def random_username():
    """
    Véletlenszerű (egyszerű) felhasználónév-generátor.
    """
    first_names = ["Anna", "Béla", "Judit", "Kata", "Laci", "Gábor", "Nóri", "Zsuzsa", "Éva", "Peti"]
    last_names = ["Kiss", "Nagy", "Szabó", "Tóth", "Horváth", "Varga", "Kovács", "Molnár"]
    return random.choice(last_names) + " " + random.choice(first_names)

def random_date_str(around_date_str):
    """
    DATE típusú kérdésnél generál egy véletlenszerű dátumot,
    ami +/- 200 nap eltéréssel lehet a helyes válasz körül.
    """
    around_date = datetime.strptime(around_date_str, "%Y-%m-%d")
    delta_days = random.randint(-200, 200)
    new_date = around_date + timedelta(days=delta_days)
    return new_date.strftime("%Y-%m-%d")

def calculate_date_score(user_input, correct_answer):
    """
    Egyszerű pontozási rendszer DATE kérdésekhez:
      - Ha a különbség napokban 0, score=100
      - Ha <30 nap eltérés, score=80
      - Ha <60 nap, score=50
      - Különben random 0-30 között
    """
    try:
        user_date = datetime.strptime(user_input, "%Y-%m-%d")
        correct_date = datetime.strptime(correct_answer, "%Y-%m-%d")
        diff = abs((user_date - correct_date).days)
        if diff == 0:
            return 100
        elif diff < 30:
            return 80
        elif diff < 60:
            return 50
        else:
            return random.randint(0, 30)
    except ValueError:
        return 0

def random_string_answer(correct_answer):
    """
    STRING típushoz "véletlenszerű" rövid válasz,
    néha helyes (kisebb eséllyel), egyébként valami random "karaktersor".
    (Alap esetben 15% -> most 40%-ra emeljük.)
    """
    chance = random.random()
    if chance < 0.40:
        return correct_answer
    letters = "abcdefghijklmnopqrstuvwxyzáéíóöőúüű"
    length = random.randint(3, 6)
    return "".join(random.choice(letters) for _ in range(length))

def score_string(user_input, correct_answer):
    """
    Egyszerű 'szöveg-hasonlóság' pontozás:
    - Ha teljesen egyezik, score=100
    - Egyébként random 0-40
    """
    if user_input.strip().lower() == correct_answer.strip().lower():
        return 100
    else:
        return random.randint(0, 40)

def random_mc_answer(question):
    """
    MC típusnál véletlenszerűen választunk az option_a..option_d közül.
    (De lásd lentebb, 30% eséllyel rögtön a helyeset adjuk vissza.)
    """
    options = [question.option_a, question.option_b, question.option_c, question.option_d]
    return random.choice(options)

def score_mc(question, user_input):
    """
    Ha megegyezik a question.correct_option által kijelölt helyes válasszal -> 100
    Egyébként 0
    """
    correct_text = None
    if question.correct_option == 'A':
        correct_text = question.option_a
    elif question.correct_option == 'B':
        correct_text = question.option_b
    elif question.correct_option == 'C':
        correct_text = question.option_c
    elif question.correct_option == 'D':
        correct_text = question.option_d

    return 100 if user_input == correct_text else 0

def generate_attempts(num_attempts=200):
    """
    Fő függvény: véletlenszerű (num_attempts) darab QuizAttempt létrehozása,
    és a Question mezők (times_asked, times_correct) frissítése.
    Magasabb eséllyel kerül be helyes válasz.
    """
    all_questions = list(Question.objects.all())

    if not all_questions:
        print("Nincsenek kérdések az adatbázisban! Előbb importáld / hozd létre őket.")
        return

    for _ in range(num_attempts):
        # Véletlen kérdés, véletlen user
        question = random.choice(all_questions)
        username = random_username()

        if question.question_type == 'DATE':
            # 30% eséllyel totál helyes a beírt dátum
            if random.random() < 0.30:
                user_input = question.correct_answer
                score = 100
            else:
                user_input = random_date_str(question.correct_answer)
                score = calculate_date_score(user_input, question.correct_answer)
            correct_option = question.correct_answer

        elif question.question_type == 'STRING':
            # Ebben a típusban a random_string_answer() már 40% eséllyel helyes
            user_input = random_string_answer(question.correct_answer)
            score = score_string(user_input, question.correct_answer)
            correct_option = question.correct_answer

        elif question.question_type == 'MC':
            # 30% eséllyel direkt a helyes opciót választjuk
            if random.random() < 0.30 and question.correct_option:
                # Kiválasztjuk a question.correct_option-nek megfelelő értéket
                if question.correct_option == 'A':
                    user_input = question.option_a
                elif question.correct_option == 'B':
                    user_input = question.option_b
                elif question.correct_option == 'C':
                    user_input = question.option_c
                elif question.correct_option == 'D':
                    user_input = question.option_d
            else:
                # Egyébként random
                user_input = random_mc_answer(question)
            score = score_mc(question, user_input)
            correct_option = question.correct_option

        else:
            # Más típusra default 0 pont
            user_input = "N/A"
            score = 0
            correct_option = ""

        # 1) Frissítjük a Question mezőit:
        question.times_asked += 1
        if score == 100:
            question.times_correct += 1
        question.save()

        # 2) Létrehozzuk a QuizAttempt rekordot
        QuizAttempt.objects.create(
            username=username,
            question=question,
            user_answer=user_input,
            correct_option=correct_option,
            score=score
        )

    print(f"{num_attempts} véletlenszerű quiz_attempt létrejött, a kérdésstatisztikák is frissültek!")

if __name__ == "__main__":

    generate_attempts(num_attempts=600)
