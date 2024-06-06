from flask import Flask, render_template, request, redirect, url_for
import csv
import io

app = Flask(__name__)

# Page d'accueil
@app.route('/')
def index():
    return render_template('index.html')

# Page d'upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        
        if file:
            # Lecture du fichier CSV
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.reader(stream)
            data = list(csv_input)
            
            # Première ligne pour les titres de colonnes
            titles = data[0]
            
            # Les autres lignes pour les données
            rows = data[1:]
            
            # Rediriger vers la page d'affichage des données
            return render_template('display_data.html', titles=titles, rows=rows)

if __name__ == '__main__':
    app.run(debug=True)

