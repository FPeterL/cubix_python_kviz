import os
import tkinter as tk
import tkinter.messagebox as messagebox
import sqlite3
import random
from datetime import datetime
from common_utils import score_string
import logging

# Logolás konfigurálása
logging.basicConfig(
    level=logging.ERROR,
    filename="quiz_app_errors.log",
    format="%(asctime)s %(levelname)s:%(message)s"
)

class QuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Quiz Játék")
        self.master.geometry("500x400")
        self.master.resizable(False, False)

        try:
            # -- EREDETI: fixen a quiz_backend/db.sqlite3 hivatkozik
            base_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(base_dir)
            db_path = os.path.join(project_dir, 'quiz_backend', 'db.sqlite3')
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            logging.exception("Database connection failed")
            messagebox.showerror("Database Error", f"Cannot connect to database: {e}")
            self.master.destroy()
            return

        self.questions = []
        self.current_index = 0
        self.current_question = None
        self.username = None
        self.correct_count = 0
        self.answer_buttons = []

        self.create_attempts_table()
        self.show_welcome()

    def create_attempts_table(self):
        try:
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
        except sqlite3.Error as e:
            logging.exception("Failed to create quiz_attempt table")
            messagebox.showerror("Database Error", f"Error creating table: {e}")

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
        self.correct_count = 0
        self.load_questions()
        self.current_index = 0
        self.load_question()

    def load_questions(self):
        try:
            self.cursor.execute("""
                SELECT id, text, question_type, option_a, option_b, option_c, option_d, correct_option, correct_answer
                FROM quiz_question
                ORDER BY RANDOM()
                LIMIT 5
            """)
            self.questions = self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.exception("Failed to load questions")
            messagebox.showerror("Database Error", f"Error loading questions: {e}")
            self.questions = []

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

        try:
            qid, text, qtype, a, b, c, d, correct_option, correct_answer = self.current_question
        except Exception as e:
            logging.exception("Error unpacking question data")
            messagebox.showerror("Error", f"Error reading question: {e}")
            return

        tk.Label(self.master, text=f"Kérdés {self.current_index + 1}:", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.master, text=text, wraplength=450, font=("Arial", 14)).pack(pady=10)

        self.answer_buttons = []
        if qtype == 'MC':
            options = [('A', a), ('B', b), ('C', c), ('D', d)]
            # random sorrendben jelennek meg a gombok
            random.shuffle(options)
            for letter, answer in options:
                btn = tk.Button(
                    self.master,
                    text=f"{answer}",
                    font=("Arial", 12),
                    command=lambda selected=answer: self.check_answer(selected)
                )
                btn.pack(fill='x', padx=20, pady=5)
                self.answer_buttons.append(btn)
        else:
            tk.Label(self.master, text="Írd be a választ:", font=("Arial", 12)).pack(pady=5)
            self.answer_entry = tk.Entry(self.master, font=("Arial", 12))
            self.answer_entry.pack(pady=5)
            tk.Button(self.master, text="Ellenőriz", font=("Arial", 12), command=self.check_answer_text).pack(pady=5)

        self.result_label = tk.Label(self.master, text="", font=("Arial", 14))
        self.result_label.pack(pady=10)

    def clear_screen(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def check_answer(self, selected):
        try:
            qid, text, qtype, a, b, c, d, correct_option, correct_answer = self.current_question
            answer_map = {'A': a, 'B': b, 'C': c, 'D': d}
            correct_text = answer_map.get(correct_option, "")

            # Letiltjuk a gombokat, hogy ne lehessen újra rákattintani
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

            # Tovább gomb
            self.continue_button = tk.Button(self.master, text="Tovább", font=("Arial", 12), command=self.next_question)
            self.continue_button.pack(pady=10)

        except Exception as e:
            logging.exception("Error in check_answer")
            messagebox.showerror("Error", f"Error processing answer: {e}")

    def check_answer_text(self):
        try:
            qid, text, qtype, a, b, c, d, correct_option, correct_answer = self.current_question
            user_input = self.answer_entry.get().strip()

            if not user_input:
                self.result_label.config(text="Kérlek, add meg a választ!")
                return

            score = 0
            result_text = ""

            # times_asked növelése
            self.cursor.execute("""
                UPDATE quiz_question
                SET times_asked = times_asked + 1
                WHERE id = ?
            """, (qid,))

            if qtype == 'DATE':
                try:
                    user_date = datetime.strptime(user_input, "%Y-%m-%d")
                    correct_date = datetime.strptime(correct_answer, "%Y-%m-%d")
                    diff_days = abs((user_date - correct_date).days)

                    if diff_days == 0:
                        score = 100
                    elif diff_days < 30:
                        score = 100
                    else:
                        months_diff = diff_days // 30
                        score = max(0, 100 - months_diff * 10)

                    result_text = f"Pontszám: {score}%. (Helyes dátum: {correct_answer})"

                except ValueError:
                    self.result_label.config(
                        text="Hibás formátum!\nKérlek, YYYY-MM-DD formátumban add meg a dátumot."
                    )
                    return

            elif qtype == 'STRING':
                # Szöveges összehasonlítás: a common_utils.py-ban lévő score_string
                score = score_string(user_input, correct_answer)
                result_text = f"Pontszám: {score}%. (Helyes válasz: {correct_answer})"

            # Letiltjuk az "Ellenőriz" gombot
            for widget in self.master.winfo_children():
                if isinstance(widget, tk.Button) and widget['text'] == "Ellenőriz":
                    widget.config(state="disabled")

            # Rögzítjük a DB-be
            self.cursor.execute("""
                INSERT INTO quiz_attempt (username, question_id, user_answer, correct_option, score)
                VALUES (?, ?, ?, ?, ?)
            """, (self.username, qid, user_input, correct_answer, score))
            self.conn.commit()

            self.result_label.config(text=result_text)
            self.correct_count += score

            # Tovább gomb
            self.continue_button = tk.Button(
                self.master, text="Tovább", font=("Arial", 12), command=self.next_question
            )
            self.continue_button.pack(pady=10)

        except Exception as e:
            logging.exception("Error in check_answer_text")
            messagebox.showerror("Error", f"Error processing text answer: {e}")

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
