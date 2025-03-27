from flask import Flask, send_from_directory, request, jsonify
import requests
import time
import sqlite3
import os
from datetime import datetime

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
        
        try:
            if method in ['GET', 'HEAD', 'OPTIONS']:
                response = requests.request(
                    method,
                    url,
                    headers=headers,
                    allow_redirects=follow_redirect,
                    timeout=timeout
                )
            else:
                response = requests.request(
                    method,
                    url,
                    headers=headers,
                    data=body,
                    allow_redirects=follow_redirect,
                    timeout=timeout
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
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-history', methods=['GET'])
def get_history():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM history ORDER BY id DESC LIMIT 50')
        history = cursor.fetchall()
        return jsonify([dict(row) for row in history])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def save_to_history(request_data, response_data):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO history (timestamp, request, response) VALUES (?, ?, ?)
        ''', (datetime.now().isoformat(), json.dumps(request_data), json.dumps(response_data)))
        db.commit()
    except Exception as e:
        print(f"Error saving history: {str(e)}")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
