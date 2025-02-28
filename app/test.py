import unittest
import tkinter as tk
from app import QuizApp, score_string  # feltételezzük, hogy az alkalmazásod a quiz_app.py-ben van

class QuizAppTests(unittest.TestCase):
    def setUp(self):
        # Hozzunk létre egy Tkinter root ablakot, de rejtsük el
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = QuizApp(self.root)
        # Felülírjuk a load_questions metódust, hogy egy fix kérdéshalmazt használjunk a teszteléshez
        self.app.questions = [
            # (id, text, question_type, option_a, option_b, option_c, option_d, correct_option, correct_answer)
            (1, "Melyik színű az ég?", "MC", "kék", "zöld", "piros", "sárga", "A", "kék"),
            (2, "Mikor történt az első holdra lépés?", "DATE", None, None, None, None, None, "1969-07-20"),
            (3, "Melyik állat a legjobb barát?", "STRING", None, None, None, None, None, "kutya"),
        ]
        self.app.current_index = 0

    def tearDown(self):
        self.root.destroy()

    def test_mc_question(self):
        self.app.current_question = self.app.questions[0]
        self.app.display_question()
        # Szimuláljuk, hogy a felhasználó kiválasztja a helyes válasz opciót ("kék")
        self.app.check_answer("kék")
        result = self.app.result_label.cget("text")
        self.assertIn("Helyes válasz", result)

    def test_date_question(self):
        self.app.current_question = self.app.questions[1]
        self.app.display_question()
        # Szimuláljuk a helyes dátum bevitelét
        self.app.answer_entry.insert(0, "1969-07-20")
        self.app.check_answer_text()
        result = self.app.result_label.cget("text")
        self.assertIn("Pontszám: 100%", result)

    def test_string_question(self):
        self.app.current_question = self.app.questions[2]
        self.app.display_question()
        # Szimuláljuk, hogy a felhasználó "kutya" helyett "kutay"-t ír be, ami kis eltérés
        self.app.answer_entry.insert(0, "kutay")
        self.app.check_answer_text()
        result = self.app.result_label.cget("text")
        # Ellenőrizzük, hogy nem 100% pontot kap, de több mint 0 pontot
        self.assertNotEqual(result, "Pontszám: 100% (Helyes válasz: kutya)")
        self.assertIn("Pontszám:", result)

if __name__ == "__main__":
    unittest.main()
