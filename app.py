from flask import Flask, send_from_directory, request, jsonify
import requests
import time

app = Flask(__name__)

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
        if not os.path.exists('/tmp/history.json'):
            with open('/tmp/history.json', 'w') as f:
                json.dump([], f)
        
        with open('/tmp/history.json', 'r') as f:
            try:
                history = json.load(f)
                if not isinstance(history, list):
                    history = []
                return jsonify(history)
            except json.JSONDecodeError:
                return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def save_to_history(request_data, response_data):
    try:
        history = []
        if os.path.exists('/tmp/history.json'):
            with open('/tmp/history.json', 'r') as f:
                try:
                    history = json.load(f)
                    if not isinstance(history, list):
                        history = []
                except json.JSONDecodeError:
                    history = []
        
        history.insert(0, {
            'timestamp': datetime.now().isoformat(),
            'request': request_data,
            'response': response_data
        })
        
        history = history[:50]
        
        with open('/tmp/history.json', 'w') as f:
            json.dump(history, f, indent=2)
            
    except Exception as e:
        print(f"Error saving history: {str(e)}")

if __name__ == '__main__':
    if not os.path.exists('/tmp/history.json'):
        with open('/tmp/history.json', 'w') as f:
            json.dump([], f)
    app.run(debug=True)
