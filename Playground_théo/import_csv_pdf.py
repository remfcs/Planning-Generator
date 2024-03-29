import csv


def creer_eleves_pdf(input_csv_file, output_pdf_file):
    # Vérifier si le fichier d'entrée existe
    if not os.path.exists(input_csv_file):
        print(f"Le fichier {input_csv_file} n'existe pas.")
        return
    
    # Ouvrir le fichier CSV en mode lecture
    with open(input_csv_file, 'r', newline='', encoding='utf-8') as csvfile:
        # Lire le contenu du fichier CSV
        csv_reader = csv.reader(csvfile)
        students = list(csv_reader)
    
    # Créer un document PDF
    doc = SimpleDocTemplate(output_pdf_file, pagesize=letter)
    elements = []

    # Mettre en forme les données dans un tableau
    data = []
    for student in students:
        data.append([student[0], student[1], student[2]])

    # Créer un tableau avec les données
    table = Table(data)

    # Définir le style du tableau
    style = TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey),
                        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0,0), (-1,0), 12),
                        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                        ('GRID', (0,0), (-1,-1), 1, colors.black)])

    table.setStyle(style)

    # Ajouter le tableau au document PDF
    elements.append(table)

    # Générer le PDF
    doc.build(elements)

    print(f"Le fichier PDF '{output_pdf_file}' a été créé avec succès.")

# Exemple d'utilisation
creer_eleves_pdf("C:/Users/theog/Desktop/4A/Semester_Project/liste_eleve_v1.csv", "C:/Users/theog/Desktop/4A/Semester_Project/liste_eleves_langues.pdf")
