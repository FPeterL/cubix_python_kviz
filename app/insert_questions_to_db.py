import sqlite3
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(base_dir)
db_path = os.path.join(project_dir, 'quiz_backend', 'db.sqlite3')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# DATE típusú kérdések: (kérdés_szöveg, helyes_dátum [YYYY-MM-DD])
date_questions = [
    ("Mikor volt az 1848-as forradalom kitörésének napja Magyarországon?", "1848-03-15"),
    ("Mikor történt a berlini fal leomlása?", "1989-11-09"),
    ("Mikor lépett először ember a Holdra?", "1969-07-20"),
    ("Mikor kiáltották ki a Magyar Köztársaságot?", "1989-10-23"),
    ("Mikor volt a mohácsi vész?", "1526-08-29"),
    ("Mikor írták alá a trianoni békeszerződést?", "1920-06-04"),
    ("Mikor kezdődött az első világháború?", "1914-07-28"),
    ("Mikor ért véget a második világháború Európában?", "1945-05-08"),
    ("Mikor fedezte fel Kolumbusz Kristóf Amerikát?", "1492-10-12"),
    ("Mikor vezette be Gutenberg a nyomtatott könyvnyomtatást?", "1455-02-23")
]

# STRING típusú kérdések: (kérdés_szöveg, helyes_szöveges_válasz)
string_questions = [
    ("Melyik város Magyarország fővárosa?", "Budapest"),
    ("Milyen színű a fű általában?", "zöld"),
    ("Milyen formájú a pizza?", "kerek"),
    ("Milyen állat védi gyakran a házat?", "kutya"),
    ("Melyik a legnagyobb tengeri emlős?", "kék bálna"),
    ("Milyen napszak következik reggel után?", "dél"),
    ("Melyik gyümölcs piros és gömbölyű?", "alma"),
    ("Melyik a legmagasabb hegy a Földön?", "Csomolungma"),
    ("Milyen nyelven beszélnek Spanyolországban?", "spanyol"),
    ("Milyen színű a flamingó?", "rózsaszín")
]

# MC típusú kérdések (kérdés_szöveg, helyes_válasz, hibás_válasz1, hibás_válasz2, hibás_válasz3)
# Megjegyzés: A beszúró függvény a correct_option='A' értéket állítja be,
# ezért mindig az első opció (option_a) lesz a helyes válasz, de a program randomizáltan írja ki.
mc_questions = [
    ("Melyik a legnagyobb kontinens?", "Ázsia", "Európa", "Afrika", "Amerika"),
    ("Melyik Magyarország hivatalos nyelve?", "magyar", "angol", "német", "francia"),
    ("Melyik állat él vízben?", "hal", "oroszlán", "tyúk", "ló"),
    ("Melyik évben kezdődött a magyar forradalom és szabadságharc?", "1848", "1867", "1956", "1789"),
    ("Melyik az ember legnagyobb belső szerve?", "máj", "tüdő", "szív", "vese"),
    ("Melyik városban található az Eiffel-torony?", "Párizs", "London", "Róma", "Berlin"),
    ("Melyik állam fővárosa Prága?", "Csehország", "Szlovákia", "Ausztria", "Lengyelország"),
    ("Melyik bolygón élünk?", "Föld", "Mars", "Vénusz", "Merkúr"),
    ("Melyik kontinensen található Magyarország?", "Európa", "Ázsia", "Afrika", "Amerika"),
    ("Melyik a legnépesebb ország a világon?", "Kína", "India", "Egyesült Államok", "Oroszország")
]


def insert_mc_question(text, option_a, option_b, option_c, option_d):
    """
    Többválasztós (MC) kérdés beszúrása az adatbázisba.
    Mivel correct_option='A', ezért az 'option_a' az egyetlen helyes válasz.
    """
    cursor.execute("""
        INSERT INTO quiz_question
        (text, question_type, option_a, option_b, option_c, option_d, correct_option, times_asked, times_correct)
        VALUES (?, 'MC', ?, ?, ?, ?, 'A', 0, 0)
    """, (text, option_a, option_b, option_c, option_d))


def insert_question(text, qtype, correct_answer):
    """
    DATE vagy STRING típusú kérdés beszúrása az adatbázisba.
    """
    cursor.execute("""
        INSERT INTO quiz_question
        (text, question_type, correct_answer, times_asked, times_correct)
        VALUES (?, ?, ?, 0, 0)
    """, (text, qtype, correct_answer))

# -- 4) A kérdések beszúrása --

# DATE típusú kérdések beszúrása
for q in date_questions:
    question_text, correct_date = q
    insert_question(question_text, "DATE", correct_date)

# STRING típusú kérdések beszúrása
for q in string_questions:
    question_text, correct_str = q
    insert_question(question_text, "STRING", correct_str)

# MC típusú kérdések beszúrása
for q in mc_questions:
    question_text, correct_ans, wrong1, wrong2, wrong3 = q
    insert_mc_question(question_text, correct_ans, wrong1, wrong2, wrong3)

# -- 5) Mentés és lezárás --
conn.commit()
conn.close()

print("A kérdések sikeresen beszúrva az adatbázisba!")
