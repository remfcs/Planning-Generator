import os
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

# Définir le dossier de téléchargement
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Créer le dossier de téléchargement s'il n'existe pas
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('start.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Récupérer les valeurs des champs de formulaire
    estimate_number_student = request.form.get('estimate_number_student')
    halfday_slot = request.form.get('halfday_slot')

    # Récupérer les fichiers uploadés
    students_files = request.files.getlist('students_files')
    level_files = request.files.getlist('level_files')

    # Enregistrer les fichiers uploadés
    saved_files = {'students_files': [], 'level_files': []}

    for file in students_files:
        if file.filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            saved_files['students_files'].append(file.filename)

    for file in level_files:
        if file.filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            saved_files['level_files'].append(file.filename)

    # Afficher les données pour vérification (peut être remplacé par une autre logique)
    return f"""
    Estimation du nombre de nouveaux étudiants: {estimate_number_student} <br>
    Nombre de demi-journées: {halfday_slot} <br>
    Fichiers étudiants téléchargés: {", ".join(saved_files['students_files'])} <br>
    Fichiers de niveau téléchargés: {", ".join(saved_files['level_files'])}
    """

if __name__ == '__main__':
    app.run(debug=True)

