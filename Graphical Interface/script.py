from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import sqlite3
import json
import os
from urllib.parse import urlparse, parse_qs

# Obtenir le répertoire du fichier script.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Définir les chemins des fichiers HTML et JS
DATABASE = os.path.join(BASE_DIR, 'test.sqlite3')
HTML_FILE = os.path.join(BASE_DIR, 'modify-student.html')
JS_FILE = os.path.join(BASE_DIR, 'modify-student.js')

class MyRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type='text/html'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self._set_headers()
            with open(HTML_FILE, 'r', encoding='utf-8') as file:
                self.wfile.write(file.read().encode('utf-8'))
        elif self.path == '/modify-student.js':
            self._set_headers('application/javascript')
            with open(JS_FILE, 'r', encoding='utf-8') as file:
                self.wfile.write(file.read().encode('utf-8'))
        else:
            self.send_error(404, "File Not Found")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        if self.path == '/add_student':
            self.add_student(data)
        elif self.path == '/delete_student':
            self.delete_student(data)
        elif self.path == '/change_student_class':
            self.change_student_class(data)
        elif self.path == '/change_teacher_time_slot':
            self.change_teacher_time_slot(data)
        else:
            self.send_error(404, "Endpoint Not Found")

    def add_student(self, data):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO students (name, first_name, promo, email, english_level, lv2, lv2_level, reduced_exam)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (data['name'], data['first_name'], data['promo'], data['email'], data['english_level'], data['lv2'], data['lv2_level'], data['reduced_exam']))
        conn.commit()
        conn.close()
        self._set_headers('application/json')
        self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))

    def delete_student(self, data):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE name = ?", (data['name'],))
        conn.commit()
        conn.close()
        self._set_headers('application/json')
        self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))

    def change_student_class(self, data):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET class = ? WHERE name = ?", (data['new_class'], data['name']))
        conn.commit()
        conn.close()
        self._set_headers('application/json')
        self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))

    def change_teacher_time_slot(self, data):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("UPDATE teachers SET time_slot = ? WHERE name = ?", (data['new_time_slot'], data['name']))
        conn.commit()
        conn.close()
        self._set_headers('application/json')
        self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=MyRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
