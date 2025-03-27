from flask import Flask, send_from_directory, request, jsonify
import requests
import sqlite3
import time
from datetime import datetime
import os

app = Flask(__name__)

DATABASE = '/tmp/history.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            request TEXT NOT NULL,
            response TEXT NOT NULL
        )
        ''')
        db.commit()

def save_to_history(request_data, response_data):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO history (timestamp, request, response) VALUES (?, ?, ?)',
                   (datetime.utcnow().isoformat(), str(request_data), str(response_data)))
    db.commit()

@app.route('/')
def serve_index():
    return send_from_directory('src', 'index.html')

@app.route('/send-request', methods=['POST'])
def send_request():
    try:
        data = request.json
        start_time = time.time()

        method = data['method']
        url = data['url']
        headers = data.get('headers', {})
        body = data.get('body', '')
        follow_redirect = data.get('followRedirect', True)
        timeout = data.get('timeout', 5000) / 1000

        if method in ['GET', 'HEAD', 'OPTIONS']:
            response = requests.request(
                method, url, headers=headers, allow_redirects=follow_redirect, timeout=timeout
            )
        else:
            response = requests.request(
                method, url, headers=headers, data=body, allow_redirects=follow_redirect, timeout=timeout
            )

        try:
            response_data = response.json()
        except ValueError:
            response_data = response.text

        formatted_response = {
            'status': response.status_code,
            'statusText': response.reason,
            'headers': dict(response.headers),
            'data': response_data,
            'responseTime': f'{(time.time() - start_time) * 1000:.2f} ms'
        }

        save_to_history(data, formatted_response)

        return jsonify({'response': formatted_response})

    except requests.exceptions.RequestException as e:
        error_response = {
            'status': 0,
            'statusText': 'Request Failed',
            'headers': {},
            'data': {'error': str(e)},
            'responseTime': f'{(time.time() - start_time) * 1000:.2f} ms'
        }
        save_to_history(data, error_response)
        return jsonify({'response': error_response})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
