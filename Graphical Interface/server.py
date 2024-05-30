from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import sqlite3
import json
import os
from urllib.parse import urlparse, parse_qs

PORT = 8000

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        base_path = os.path.dirname(__file__)
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            home_path = os.path.join(base_path, 'home.html')
            with open(home_path, 'r', encoding='utf-8') as file:
                self.wfile.write(file.read().encode())

        elif path == '/students':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            conn = sqlite3.connect(os.path.join(base_path, 'data_copy.sqlite3'))
            c = conn.cursor()

            query_str = 'SELECT Student.Name, Student.Surname, Student.Email, Student.Class, Student.LV1, Student.GROUP_LV1, Teachers.name as Teachers FROM Student JOIN groups ON Student.group_id = groups.id JOIN Teachers ON groups.teacher_id = teacher.id WHERE 1=1'
            params = []

            if 'name' in query:
                name = query['name'][0]
                query_str += " AND (Student.Name LIKE ? OR Student.Surname LIKE ?)"
                params.extend([f"%{name}%", f"%{name}%"])
            if 'niveau' in query:
                niveau = query['niveau'][0]
                query_str += " AND Student.Class = ?"
                params.append(niveau)
            if 'professeur' in query:
                professeur = query['professeur'][0]
                query_str += " AND Teachers.name = ?"
                params.append(professeur)
            if 'langue' in query:
                langue = query['langue'][0]
                query_str += " AND Student.LV1 = ?"
                params.append(langue)

            c.execute(query_str, params)
            students = c.fetchall()
            conn.close()

            self.wfile.write(json.dumps([dict(zip([column[0] for column in c.description], row)) for row in students]).encode())

        elif path == '/teachers':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            conn = sqlite3.connect(os.path.join(base_path, 'data_copy.sqlite3'))
            c = conn.cursor()
            c.execute("SELECT DISTINCT name FROM Teachers")
            teachers = c.fetchall()
            conn.close()

            self.wfile.write(json.dumps([row[0] for row in teachers]).encode())

        elif path == '/languages':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            conn = sqlite3.connect(os.path.join(base_path, 'data_copy.sqlite3'))
            c = conn.cursor()
            c.execute("SELECT DISTINCT LV1 FROM Student")
            languages = c.fetchall()
            conn.close()

            self.wfile.write(json.dumps([row[0] for row in languages]).encode())

        elif path.endswith('.js'):
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.end_headers()

            file_path = os.path.join(base_path, self.path.lstrip('/'))
            with open(file_path, 'r', encoding='utf-8') as file:
                self.wfile.write(file.read().encode())

        elif path.endswith('.css'):
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()

            file_path = os.path.join(base_path, self.path.lstrip('/'))
            with open(file_path, 'r', encoding='utf-8') as file:
                self.wfile.write(file.read().encode())

        else:
            self.send_response(404)
            self.end_headers()

Handler = MyHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
