import unittest
import tkinter as tk
import sqlite3 as real_sqlite3
from unittest.mock import patch
from app.quiz_app import QuizApp

class TestQuizApp(unittest.TestCase):
    def setUp(self):
        """
        Minden teszt előtt:
         - Létrehozunk egy rejtett Tk ablakot,
         - Kipatch-eljük a quiz_app.py modulban az sqlite3.connect hívást,
           hogy ne a valódi db.sqlite3 fájlt nyissa, hanem in-memory DB-t.
         - Létrehozzuk a QuizApp példányt,
         - Létrehozzuk a szükséges táblákat, és beletöltünk pár tesztkérdést.
        """
        self.root = tk.Tk()
        self.root.withdraw()

        self.real_connect = real_sqlite3.connect

        self.patcher = patch('app.quiz_app.sqlite3.connect', side_effect=self.mock_connect)
        self.mocked_connect = self.patcher.start()

        self.app = QuizApp(self.root)

        self.create_test_tables()
        self.insert_test_questions()

    def tearDown(self):
        """
        Teszt után:
         - Bezárjuk a Tk ablakot,
         - Leállítjuk a patch-et.
        """
        self.root.destroy()
        self.patcher.stop()

    def mock_connect(self, db_path):
        """
        A patchelt függvény:
         - Bármilyen bejövő db_path esetén
           a valódi sqlite3.connect(":memory:")-vel tér vissza.
        """
        return self.real_connect(":memory:")

    def create_test_tables(self):
        """
        Létrehozzuk a quiz_question és quiz_attempt táblákat
        az in-memory DB-ben, mert ott alapból még semmi nincs.
        """
        cursor = self.app.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_question (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                question_type TEXT,
                option_a TEXT,
                option_b TEXT,
                option_c TEXT,
                option_d TEXT,
                correct_option TEXT,
                correct_answer TEXT,
                times_asked INTEGER DEFAULT 0,
                times_correct INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_attempt (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                question_id INTEGER,
                user_answer TEXT,
                correct_option TEXT,
                score REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.app.conn.commit()

    def insert_test_questions(self):
        """
        Beteszünk 3 tesztkérdést (MC, DATE, STRING).
        """
        cursor = self.app.conn.cursor()

        cursor.execute("""
            INSERT INTO quiz_question (text, question_type, option_a, option_b, option_c, option_d, correct_option, correct_answer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("Melyik színű az ég?", "MC", "kék", "zöld", "piros", "sárga", "A", "kék"))

        # Dátum típusú kérdés
        cursor.execute("""
            INSERT INTO quiz_question (text, question_type, option_a, option_b, option_c, option_d, correct_option, correct_answer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("Mikor történt az első holdra lépés?", "DATE", None, None, None, None, None, "1969-07-20"))

        # Sztring típusú kérdés
        cursor.execute("""
            INSERT INTO quiz_question (text, question_type, option_a, option_b, option_c, option_d, correct_option, correct_answer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ("Melyik állat a legjobb barát?", "STRING", None, None, None, None, None, "kutya"))

        self.app.conn.commit()

    def test_start_quiz_with_username(self):
        """
        - Beírunk egy felhasználónevet,
        - Meghívjuk a start_quiz()-et,
        - Ellenőrizzük, hogy a betöltött kérdések száma 3 lett-e.
        """
        self.app.username_entry.insert(0, "TesztElek")
        self.app.start_quiz()
        self.assertEqual(self.app.username, "TesztElek")
        self.assertEqual(len(self.app.questions), 3, "Nem 3 kérdés töltődött be!")

    def test_mc_question_correct(self):
        """
        Egyszerűen beállítjuk, hogy 1 MC kérdés legyen (helyes opció: 'kék'),
        majd keressük a kék gombot, rákattintunk (invoke), és nézzük,
        hogy Helyes válasz jelenik-e meg a result_label-ben.
        """
        self.app.questions = [
            (1, "Melyik színű az ég?", "MC", "kék", "zöld", "piros", "sárga", "A", "kék"),
        ]
        self.app.current_index = 0
        self.app.current_question = self.app.questions[0]

        self.app.display_question()
        correct_btn = None
        for btn in self.app.answer_buttons:
            if btn.cget("text") == "kék":
                correct_btn = btn
                break

        self.assertIsNotNone(correct_btn, "Helyes válasz gombja nem található!")
        correct_btn.invoke()

        result = self.app.result_label.cget("text")
        self.assertIn("Helyes válasz", result)

    def test_date_question_correct(self):
        """
        DATE típusú kérdés helyes formátummal.
        Elvárt, hogy Pontszám: 100% legyen.
        """
        self.app.questions = [
            (2, "Mikor történt az első holdra lépés?", "DATE", None, None, None, None, None, "1969-07-20")
        ]
        self.app.current_index = 0
        self.app.current_question = self.app.questions[0]

        self.app.display_question()
        self.app.answer_entry.insert(0, "1969-07-20")
        self.app.check_answer_text()

        result = self.app.result_label.cget("text")
        self.assertIn("Pontszám: 100%", result)

    def test_string_question_partial(self):
        """
        STRING típusú kérdés: correct_answer='kutya',
        user_input='kutay'.
        A common_utils.score_string függvény valamekkora pontszámot
        (0 < x < 100) adjon. Tehát ne legyen 0%, de ne is 100%.
        """
        self.app.questions = [
            (3, "Melyik állat a legjobb barát?", "STRING", None, None, None, None, None, "kutya")
        ]
        self.app.current_index = 0
        self.app.current_question = self.app.questions[0]

        self.app.display_question()
        self.app.answer_entry.insert(0, "kutay")
        self.app.check_answer_text()

        result = self.app.result_label.cget("text")

        self.assertNotIn("Pontszám: 100%", result)
        self.assertIn("Pontszám:", result)


if __name__ == "__main__":
    unittest.main()
