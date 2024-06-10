import pdfkit
import logging
import os
import sqlite3
import csv
import io
import pandas as pd
from flask import send_file, make_response, jsonify

# Configuration PDF
project_dir = os.path.dirname(os.path.abspath(__file__))
path_wkhtmltopdf = os.path.join(project_dir, 'wkhtmltopdf', 'bin', 'wkhtmltopdf.exe')
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

DATABASE_PATH = './data/database.sqlite3'

def get_student_details(name=None, niveau=None, professeur=None, langue=None, group_lv1=None):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    query = """
    SELECT s.NAME, s.SURNAME, s.EMAIL, s.SCHOOL_YEAR, lg.ID_COURSE, c.Language, t.NAME AS TeacherName, t.SURNAME AS TeacherSurname
    FROM Student s
    LEFT JOIN List_Groups_Students lg ON s.EMAIL = lg.ID_STUDENT
    LEFT JOIN Courses c ON lg.ID_COURSE = c.ID_COURSE
    LEFT JOIN Teachers t ON c.ID_Teacher = t.ID_Teacher
    WHERE 1=1
    """
    params = []

    if name:
        query += " AND LOWER(s.NAME) LIKE ?"
        params.append(f"%{name}%")
    if niveau:
        query += " AND s.SCHOOL_YEAR = ?"
        params.append(niveau)
    if professeur:
        query += " AND (t.NAME || ' ' || t.SURNAME) = ?"
        params.append(professeur)
    if langue:
        query += " AND c.Language = ?"
        params.append(langue)
    if group_lv1:
        query += " AND lg.ID_COURSE = ?"
        params.append(group_lv1)

    cursor.execute(query, params)
    rows = cursor.fetchall()

    students = []
    for row in rows:
        student = {
            "Surname": row[0],
            "Name": row[1],
            "Email": row[2],
            "Class": row[3],
            "GROUP_LV1": row[4],
            "Language": row[5],
            "TeacherName": row[6],
            "TeacherSurname": row[7]
        }
        students.append(student)

    conn.close()
    logging.debug(f"Retrieved students: {students}")
    return students

def generate_group_pdf(group_id):
    students = get_student_details(group_lv1=group_id)
    html_content = f"""
    <html>
    <head>
        <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1, h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 0.9em;
            background-color: #f2f2f2;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px 15px;
            text-align: left;
        }}
        th {{
            background-color: #2980b9;
            color: white;
            text-transform: uppercase;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f1f1f1;
        }}
        </style>
    </head>
    <body>
        <h1>Group {group_id}</h1>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Surname</th>
                    <th>Email</th>
                    <th>Class</th>
                </tr>
            </thead>
            <tbody>
    """
    for student in students:
        html_content += f"""
                <tr>
                    <td>{student['Name']}</td>
                    <td>{student['Surname']}</td>
                    <td>{student['Email']}</td>
                    <td>{student['Class']}</td>
                </tr>
        """
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    output_path = f"./group_{group_id}.pdf"
    absolute_output_path = os.path.abspath(output_path)

    pdfkit.from_string(html_content, output_path, configuration=config)

    if not os.path.exists(absolute_output_path):
        return "Failed to create PDF file", 500

    return send_file(absolute_output_path, as_attachment=True, download_name=f'group_{group_id}.pdf')

def generate_professors_pdf():
    professors = get_professors_with_groups()
    html_content = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; color: #333; }
            h1 { color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 0.9em; background-color: #f2f2f2; }
            th, td { border: 1px solid #ddd; padding: 12px 15px; text-align: left; }
            th { background-color: #2980b9; color: white; text-transform: uppercase; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            tr:hover { background-color: #f1f1f1; }
        </style>
    </head>
    <body>
        <h1>Professors List</h1>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Surname</th>
                    <th>Email</th>
                    <th>Subject</th>
                    <th>Availability</th>
                    <th>Groups</th>
                </tr>
            </thead>
            <tbody>
    """
    for professor in professors:
        name, surname, email, subject, availability, groups = professor
        availability = "<br>".join(set(availability.split(','))) if availability else ""
        if groups:
            groups_list = groups.split(',')
            unique_groups = list(dict.fromkeys(groups_list))
            groups_html = "<br>".join(unique_groups)
        else:
            groups_html = ""
        html_content += f"""
            <tr>
                <td>{name}</td>
                <td>{surname}</td>
                <td>{email}</td>
                <td>{subject}</td>
                <td>{availability}</td>
                <td>{groups_html}</td>
            </tr>
    """
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    pdf = pdfkit.from_string(html_content, False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=professors_list.pdf'
    return response

def generate_professor_pdf(professor_name):
    professor_details = get_professor_details(professor_name=professor_name)
    if not professor_details:
        return "No professor details found", 404

    html_content = f"""
    <html>
    <head>
        <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1, h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 0.9em;
            background-color: #f2f2f2;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px 15px;
            text-align: left;
        }}
        th {{
            background-color: #2980b9;
            color: white;
            text-transform: uppercase;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f1f1f1;
        }}
        </style>
    </head>
    <body>
        <h1>Professor {professor_name}</h1>
        <h2>Details</h2>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Surname</th>
                    <th>Email</th>
                    <th>Subject</th>
                    <th>Availability</th>
                </tr>
            </thead>
            <tbody>
    """
    for detail in professor_details:
        html_content += f"""
        <tr>
            <td>{detail['name']}</td>
            <td>{detail['surname']}</td>
            <td>{detail['email']}</td>
                        <td>{detail['subject']}</td>
            <td>{detail['availability'].replace(",", ", ")}</td>
        </tr>
        """
    html_content += """
            </tbody>
        </table>
        <h2>Groups</h2>
        <table>
            <thead>
                <tr>
                    <th>Group</th>
                    <th>Day</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
    """
    groups = get_professor_groups(professor_name)
    for group in groups:
        html_content += f"""
        <tr>
            <td>{group[0]}</td>
            <td>{group[1]}</td>
            <td>{group[2]}</td>
        </tr>
        """
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    pdf = pdfkit.from_string(html_content, False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=professor_{professor_name}.pdf'
    return response

def get_professors_with_groups():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT T.name, T.surname, T.mail, T.Subject, 
               GROUP_CONCAT(DISTINCT A.Day || ' ' || A.Hour) as availabilities,
               GROUP_CONCAT(DISTINCT C.ID_COURSE || ' (' || A.Day || ' ' || A.Hour || ')') as groups
        FROM Teachers T
        LEFT JOIN Availability_Teachers AT ON T.ID_Teacher = AT.ID_Teacher
        LEFT JOIN Availabilities A ON AT.ID_Availability = A.ID_Availability
        LEFT JOIN Courses C ON T.ID_Teacher = C.ID_Teacher
        GROUP BY T.name, T.surname, T.mail, T.Subject
    """)
    professors = cursor.fetchall()
    conn.close()
    return professors

def get_professor_details(professor_name):
    if not professor_name:
        return []

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    name_parts = professor_name.split()
    if len(name_parts) < 2:
        return []  # Nom de professeur invalide

    first_name = name_parts[0]
    last_name = name_parts[1]

    cursor.execute("""
        SELECT t.name, t.surname, t.mail, t.Subject, 
               GROUP_CONCAT(A.Day || ' ' || A.Hour) as availabilities
        FROM Teachers t
        LEFT JOIN Availability_Teachers AT ON t.ID_Teacher = AT.ID_Teacher
        LEFT JOIN Availabilities A ON AT.ID_Availability = A.ID_Availability
        WHERE t.name = ? AND t.surname = ?
        GROUP BY t.name, t.surname, t.mail, t.Subject
    """, (first_name, last_name))

    rows = cursor.fetchall()
    conn.close()

    professors = []
    for row in rows:
        professors.append({
            'name': row[0],
            'surname': row[1],
            'email': row[2],
            'subject': row[3],
            'availability': row[4]
        })

    return professors

def get_professor_groups(professor_name):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.ID_COURSE, a.Day, a.Hour
        FROM Courses c
        JOIN Teachers t ON c.ID_Teacher = t.ID_Teacher
        JOIN Availabilities a ON c.ID_Availability = a.ID_Availability
        WHERE t.name || ' ' || t.surname = ?
    """, (professor_name,))

    groups = cursor.fetchall()
    conn.close()

    return groups

def generate_professors_csv():
    professors = get_professors_with_groups()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Surname", "Email", "Subject", "Availability", "Groups"])
    for professor in professors:
        name, surname, email, subject, availability, groups = professor
        availability = availability.replace(",", ", ") if availability else ""
        if groups:
            groups_list = groups.split(',')
            unique_groups = list(dict.fromkeys(groups_list))
            groups = ', '.join(unique_groups)
        else:
            groups = ""
        writer.writerow([name, surname, email, subject, availability, groups])
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=professors_list.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

def generate_professor_csv(professor_name):
    professor_details = get_professor_details(professor_name=professor_name)
    if not professor_details:
        return "No professor details found", 404

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Surname", "Email", "Subject", "Availability"])
    for detail in professor_details:
        writer.writerow([detail['name'], detail['surname'], detail['email'], detail['subject'], detail['availability'].replace(",", ", ")])
    
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=professor_{professor_name}.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

def generate_group_csv(group_id):
    students = get_student_details(group_lv1=group_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Surname", "Name", "Email", "Class", "GROUP_LV1", "Language", "TeacherName", "TeacherSurname"])
    for student in students:
        writer.writerow([student["Surname"], student["Name"], student["Email"], student["Class"], student["GROUP_LV1"], student["Language"], student["TeacherName"], student["TeacherSurname"]])
    output.seek(0)
    response = make_response(output.getvalue())
    logging.debug(f"Setting Content-Disposition header for group {group_id}")
    response.headers['Content-Disposition'] = f'attachment; filename="group_{group_id}.csv"'
    response.headers['Content-Type'] = 'text/csv'
    return response

def export_all_groups():
    groups_response = get_groups()
    if groups_response.status_code != 200:
        return "Failed to get groups", 500

    groups = groups_response.get_json()
    if not groups:
        return "No groups found", 400

    html_content = """
    <html>
    <head>
        <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
            color: #333;
        }
        h1, h2 {
            color: #2c3e50;
            border-bottom: 2px solid #2c3e50;
            padding-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 0.9em;
            background-color: #f2f2f2;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px 15px;
            text-align: left;
        }
        th {
            background-color: #2980b9;
            color: white;
            text-transform: uppercase;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
        </style>
    </head>
    <body>
    <h1>All Groups</h1>
    """

    for group_id in groups:
        students = get_student_details(group_lv1=group_id)
        html_content += f"""
        <h2>Group {group_id}</h2>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Surname</th>
                    <th>Email</th>
                    <th>Class</th>
                </tr>
            </thead>
            <tbody>
        """
        for student in students:
            html_content += f"""
                <tr>
                    <td>{student['Name']}</td>
                    <td>{student['Surname']}</td>
                    <td>{student['Email']}</td>
                    <td>{student['Class']}</td>
                </tr>
            """
        html_content += """
            </tbody>
        </table>
        """
    html_content += """
    </body>
    </html>
    """

    output_path = "./all_groups.pdf"
    absolute_output_path = os.path.abspath(output_path)

    pdfkit.from_string(html_content, output_path, configuration=config)

    if not os.path.exists(absolute_output_path):
        return "Failed to create PDF file", 500

    return send_file(absolute_output_path, as_attachment=True, download_name='all_groups.pdf')

def export_all_groups_csv():
    response = get_groups()
    if response.status_code != 200:
        logging.error(f"Failed to get groups: {response.status_code}")
        return "Failed to get groups", 500

    groups = response.get_json()
    if not groups:
        logging.error("No groups found")
        return "No groups found", 400

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["GroupID", "Surname", "Name", "Email", "Class", "GROUP_LV1", "Language", "TeacherName", "TeacherSurname", "Day", "Time"])

    for group in groups:
        students = get_student_details(group_lv1=group)
        for student in students:
            teacher_name = student.get('TeacherName', 'Unknown')
            teacher_surname = student.get('TeacherSurname', 'Unknown')
            day = student.get('Day', 'Unknown')  # Modify this if 'Day' is not included in student details
            time = student.get('Hour', 'Unknown')  # Modify this if 'Hour' is not included in student details
            writer.writerow([group, student['Surname'], student['Name'], student['Email'], student['Class'], student['GROUP_LV1'], student['Language'], teacher_name, teacher_surname, day, time])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=all_groups.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

def generate_group_excel(group_id):
    students = get_student_details(group_lv1=group_id)
    df = pd.DataFrame(students)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Group Data')
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=group_{group_id}.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response

def export_all_groups_excel():
    response = get_groups()
    if response.status_code != 200:
        logging.error(f"Failed to get groups: {response.status_code}")
        return "Failed to get groups", 500

    groups = response.get_json()
    if not groups:
        logging.error("No groups found")
        return "No groups found", 400

    all_data = []
    for group in groups:
        students = get_student_details(group_lv1=group)
        for student in students:
            all_data.append([group] + list(student.values()))

    df = pd.DataFrame(all_data, columns=["GroupID", "Surname", "Name", "Email", "Class", "GROUP_LV1", "Language", "TeacherName", "TeacherSurname"])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='All Groups Data')
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=all_groups.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response

def generate_professor_excel(professor_name):
    professors = get_professor_details(professor_name=professor_name)
    if not professors:
        return "No professor details found", 404
    
    df = pd.DataFrame(professors)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Professor Data')
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=professor_{professor_name}.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response

def export_all_professors_excel():
    professors = get_professors_with_groups()
    all_data = []
    for professor in professors:
        all_data.append(list(professor))

    df = pd.DataFrame(all_data, columns=["Name", "Surname", "Email", "Subject", "Availability", "Groups"])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Professors Data')
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=professors_list.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response

def get_groups():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    query = "SELECT DISTINCT ID_COURSE FROM List_Groups_Students"
    cursor.execute(query)
    groups = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(groups)
