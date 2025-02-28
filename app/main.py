# app/main.py
import tkinter as tk
from quiz_app import QuizApp
from django_utils import start_django_server

"""
Elindítja a Django szervert és az applikációt.
"""

# Django szerver indítása
django_process = start_django_server()

root = tk.Tk()
app = QuizApp(root)

def on_closing():
    if django_process is not None:
        django_process.terminate()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
