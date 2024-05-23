from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import sqlite3
import json
import os

PORT = 8000

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        base_path = os.path.dirname(__file__)
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            home_path = os.path.join(base_path, 'home.html')
            with open(home_path, 'r', encoding='utf-8') as file:
                self.wfile.write(file.read().encode())
        elif self.path == '/students':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            conn = sqlite3.connect(os.path.join(base_path, 'data_copy.sqlite3'))
            c = conn.cursor()
            c.execute('SELECT Name, Surname, Email, Class, LV1, GROUP_LV1 FROM Student ORDER BY GROUP_LV1')
            students = c.fetchall()
            conn.close()

            self.wfile.write(json.dumps(students).encode())
        elif self.path.startswith('/students?name='):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            student_name = self.path[len('/students?name='):]

            conn = sqlite3.connect(os.path.join(base_path, 'data_copy.sqlite3'))
            c = conn.cursor()
            c.execute('SELECT Name, Surname, Email, Class, LV1, GROUP_LV1 FROM Student WHERE Name = ?', (student_name,))
            student = c.fetchone()
            conn.close()

            self.wfile.write(json.dumps(student).encode())
        elif self.path.endswith('.js'):
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.end_headers()

            file_path = os.path.join(base_path, self.path.lstrip('/'))
            with open(file_path, 'r', encoding='utf-8') as file:
                self.wfile.write(file.read().encode())
        elif self.path.endswith('.css'):
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
