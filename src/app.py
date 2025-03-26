from flask import Flask, render_template, jsonify, request
import requests
from requests.exceptions import RequestException
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

requests_history = []

@app.route('/')
def serve_index():
    return render_template('../index.html')

@app.route('/api/proxy', methods=['POST'])
def proxy_request():
    try:
        data = request.json
        req_data = {
            'timestamp': datetime.now().isoformat(),
            'method': data['method'],
            'url': data['url'],
            'headers': data.get('headers', {}),
            'body': data.get('body', ''),
            'timeout': data.get('timeout', 5),
            'follow_redirects': data.get('follow_redirects', True)
        }

        req_args = {
            'method': req_data['method'],
            'url': req_data['url'],
            'headers': req_data['headers'],
            'data': req_data['body'],
            'timeout': req_data['timeout'],
            'allow_redirects': req_data['follow_redirects']
        }

        start_time = datetime.now()
        response = requests.request(**req_args)
        response_time = (datetime.now() - start_time).total_seconds() * 1000

        try:
            response_body = response.json()
        except ValueError:
            response_body = response.text

        result = {
            'status': response.status_code,
            'status_text': response.reason,
            'headers': dict(response.headers),
            'body': response_body,
            'response_time': response_time
        }

        requests_history.insert(0, {
            'request': req_data,
            'response': result,
            'timestamp': req_data['timestamp']
        })
        
        if len(requests_history) > 50:
            requests_history.pop()

        return jsonify(result)

    except RequestException as e:
        return jsonify({
            'error': str(e),
            'status': 500,
            'status_text': 'Request Failed'
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(requests_history)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
