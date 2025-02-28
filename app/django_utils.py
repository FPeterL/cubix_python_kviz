import os
import subprocess
import sys
import time

def start_django_server():
    """
    Elindítja a Django szervert egy külön folyamatban.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(base_dir)
    manage_py = os.path.join(project_dir, 'quiz_backend', "manage.py")

    process = subprocess.Popen(
        [sys.executable, manage_py, 'runserver'],
        cwd=project_dir
    )
    time.sleep(3)  # Rövid várakozás, hogy a szerver elinduljon
    return process
