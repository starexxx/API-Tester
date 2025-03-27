from flask import Flask, send_from_directory, request, jsonify
import requests
import time

app = Flask(__name__)

@app.route('/')
def serve_index():
    return send_from_directory('src', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('src', path)

@app.route('/send-request', methods=['POST'])
def send_request():
    try:
        data = request.json
        start_time = time.time()
        
        response = requests.request(
            data['method'],
            data['url'],
            headers=data.get('headers', {}),
            data=data.get('body', ''),
            timeout=10
        )
        
        try:
            response_data = response.json()
        except ValueError:
            response_data = response.text
            
        return jsonify({
            'status': response.status_code,
            'data': response_data,
            'time': f'{(time.time()-start_time)*1000:.2f}ms'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
