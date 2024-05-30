import webbrowser
import threading
import time
from flask import Flask, render_template
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-script')
def run_script():
    result = subprocess.run(['python', 'script.py'], capture_output=True, text=True)
    return f"<pre>{result.stdout}</pre>"

def open_browser():
    time.sleep(1)  # Attendre une seconde pour s'assurer que le serveur a démarré
    webbrowser.open('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # Démarrer un thread pour ouvrir le navigateur
    threading.Thread(target=open_browser).start()
    app.run(debug=True)
