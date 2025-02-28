import os
import tkinter as tk
import tkinter.messagebox as messagebox
import sqlite3
import random
from datetime import datetime
from common_utils import score_string

class QuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Quiz Játék")
        # Fix ablakméret: 500x400, ne lehessen átméretezni
        self.master.geometry("500x400")
        self.master.resizable(False, False)

        # Az app.py aktuális könyvtárának meghatározása (project/app)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # A projekt gyökérkönyvtárának meghatározása (egy szinttel feljebb, project)
        project_dir = os.path.dirname(base_dir)
        # Az adatbázis elérési útjának összeállítása a project/quiz_backend/db.sqlite3 alapján
        db_path = os.path.join(project_dir, 'quiz_backend', 'db.sqlite3')
        # Kapcsolódás az SQLite adatbázishoz
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        self.questions = []      # A lekérdezett 5 kérdés listája
        self.current_index = 0   # Az aktuális kérdés sorszáma
        self.current_question = None
        self.username = None
        self.correct_count = 0   # Összesített pontszám
        self.answer_buttons = [] # Referenciák az opció gombokra

        # Létrehozzuk a quiz_attempt táblát, ha még nem létezik
        self.create_attempts_table()
        # Elindítjuk az üdvözlő képernyőt
        self.show_welcome()

    def create_attempts_table(self):
        self.cursor.execute("""
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
        self.conn.commit()

    def show_welcome(self):
        self.clear_screen()
        tk.Label(self.master, text="Üdvözlünk a Quiz Játékban!", font=("Arial", 16)).pack(pady=20)
        tk.Label(self.master, text="Kérlek, add meg a neved:", font=("Arial", 12)).pack(pady=5)
        self.username_entry = tk.Entry(self.master, font=("Arial", 12))
        self.username_entry.pack(pady=5)
        tk.Button(self.master, text="Start", font=("Arial", 12), command=self.start_quiz).pack(pady=20)

    def start_quiz(self):
        self.username = self.username_entry.get().strip()
        if not self.username:
            messagebox.showerror("Hiba", "Kérlek, add meg a neved!")
            return
        self.correct_count = 0  # új kvíz esetén visszaállítjuk a pontszámot
        self.load_questions()
        self.current_index = 0
        self.load_question()

    def load_questions(self):
        # Lekérjük 5 véletlenszerű kérdést a megfelelő mezőkkel
        self.cursor.execute("""
            SELECT id, text, question_type, option_a, option_b, option_c, option_d, correct_option, correct_answer
            FROM quiz_question
            ORDER BY RANDOM()
            LIMIT 5
        """)
        self.questions = self.cursor.fetchall()

    def load_question(self):
        self.clear_screen()
        if self.current_index < len(self.questions):
            self.current_question = self.questions[self.current_index]
            self.display_question()
        else:
            self.show_final()

    def display_question(self):
        if not self.current_question:
            tk.Label(self.master, text="Nincsenek kérdések az adatbázisban!").pack()
            return

        # Kicsomagoljuk a kérdés adatait:
        # 0: id, 1: text, 2: question_type, 3: option_a, 4: option_b, 5: option_c, 6: option_d, 7: correct_option, 8: correct_answer
        qid, text, qtype, a, b, c, d, correct_option, correct_answer = self.current_question

        tk.Label(self.master, text=f"Kérdés {self.current_index + 1}:", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.master, text=text, wraplength=450, font=("Arial", 14)).pack(pady=10)

        self.answer_buttons = []
        if qtype == 'MC':
            # Multiple Choice: opciók véletlenszerű sorrendben
            options = [('A', a), ('B', b), ('C', c), ('D', d)]
            random.shuffle(options)
            for letter, answer in options:
                btn = tk.Button(self.master, text=f"{answer}", font=("Arial", 12),
                                command=lambda selected=answer: self.check_answer(selected))
                btn.pack(fill='x', padx=20, pady=5)
                self.answer_buttons.append(btn)
        else:
            # DATE vagy STRING típus: szövegbeviteli mező
            tk.Label(self.master, text="Írd be a választ:", font=("Arial", 12)).pack(pady=5)
            self.answer_entry = tk.Entry(self.master, font=("Arial", 12))
            self.answer_entry.pack(pady=5)
            tk.Button(self.master, text="Ellenőriz", font=("Arial", 12), command=self.check_answer_text).pack(pady=5)

        # Visszajelzés címke
        self.result_label = tk.Label(self.master, text="", font=("Arial", 14))
        self.result_label.pack(pady=10)

    def clear_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def check_answer(self, selected):
        """MC típusú kérdés esetén hívódik meg."""
        qid, text, qtype, a, b, c, d, correct_option, correct_answer = self.current_question
        # Mapping az eredeti opciókhoz
        answer_map = {'A': a, 'B': b, 'C': c, 'D': d}
        correct_text = answer_map.get(correct_option, "")
        for btn in self.answer_buttons:
            btn.config(state="disabled")
        self.cursor.execute("UPDATE quiz_question SET times_asked = times_asked + 1 WHERE id = ?", (qid,))
        if selected.lower() == correct_text.lower():
            self.cursor.execute("UPDATE quiz_question SET times_correct = times_correct + 1 WHERE id = ?", (qid,))
            result_text = "Helyes válasz!"
            score = 100
            self.correct_count += score
        else:
            result_text = f"Helytelen válasz! A helyes válasz: {correct_text}"
            score = 0
        self.cursor.execute("""
            INSERT INTO quiz_attempt (username, question_id, user_answer, correct_option, score)
            VALUES (?, ?, ?, ?, ?)
        """, (self.username, qid, selected, correct_option, score))
        self.conn.commit()
        self.result_label.config(text=result_text)
        self.continue_button = tk.Button(self.master, text="Tovább", font=("Arial", 12), command=self.next_question)
        self.continue_button.pack(pady=10)

    def check_answer_text(self):
        """DATE vagy STRING típusú kérdés esetén hívódik meg."""
        qid, text, qtype, a, b, c, d, correct_option, correct_answer = self.current_question
        user_input = self.answer_entry.get().strip()

        # Üres input ellenőrzése
        if not user_input:
            self.result_label.config(text="Kérlek, add meg a választ!")
            return

        # Tiltsuk le az "Ellenőriz" gombot
        for widget in self.master.winfo_children():
            if isinstance(widget, tk.Button) and widget['text'] == "Ellenőriz":
                widget.config(state="disabled")

        self.cursor.execute("UPDATE quiz_question SET times_asked = times_asked + 1 WHERE id = ?", (qid,))
        score = 0
        result_text = ""
        if qtype == 'DATE':
            try:
                user_date = datetime.strptime(user_input, "%Y-%m-%d")
                correct_date = datetime.strptime(correct_answer, "%Y-%m-%d")
                diff_days = abs((user_date - correct_date).days)
                # Pontozás: pontos egyezés -> 100, ha kevesebb, mint 30 nap eltérés -> 100,
                # egyébként minden 30 nap eltérés után 10 pont levonás
                if diff_days == 0:
                    score = 100
                elif diff_days < 30:
                    score = 100
                else:
                    months_diff = diff_days // 30
                    score = max(0, 100 - months_diff * 10)
                result_text = f"Pontszám: {score}%. (Helyes dátum: {correct_answer})"
            except Exception as e:
                score = 0
                result_text = "Hibás formátum! Használd a YYYY-MM-DD formátumot."
        elif qtype == 'STRING':
            score = score_string(user_input, correct_answer)
            result_text = f"Pontszám: {score}%. (Helyes válasz: {correct_answer})"

        self.correct_count += score
        self.cursor.execute("""
            INSERT INTO quiz_attempt (username, question_id, user_answer, correct_option, score)
            VALUES (?, ?, ?, ?, ?)
        """, (self.username, qid, user_input, correct_answer, score))
        self.conn.commit()
        self.result_label.config(text=result_text)
        self.continue_button = tk.Button(self.master, text="Tovább", font=("Arial", 12), command=self.next_question)
        self.continue_button.pack(pady=10)

    def next_question(self):
        self.current_index += 1
        self.load_question()

    def show_final(self):
        self.clear_screen()
        total = len(self.questions)
        avg_score = round(self.correct_count / total, 2) if total else 0
        tk.Label(self.master, text="A kvíz véget ért!", font=("Arial", 16)).pack(pady=20)
        tk.Label(self.master, text=f"Összpontszám: {self.correct_count}", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.master, text=f"Átlagos pontszázad: {avg_score}%", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.master, text="Újra", font=("Arial", 12), command=self.show_welcome).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
