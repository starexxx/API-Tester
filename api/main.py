from flask import Flask, render_template_string, request, jsonify
import requests
import json
import time
import os
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Starexx API Tester</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;500;600&display=swap');
        @import url('https://fonts.googleapis.com/icon?family=Material+Icons');
        :root { --primary: #007AFF; --secondary: #8E8E93; --background: #F2F2F7; --surface: #FFFFFF; --text: #1C1C1E; --text-secondary: #636366; --ripple: rgba(0, 122, 255, 0.15); --border: #C6C6C8; --danger: #FF3B30; --success: #34C759; --warning: #FF9500; }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif; -webkit-tap-highlight-color: transparent; }
        body { background: var(--background); color: var(--text); padding-bottom: 20px; }
        .header { background: var(--surface); color: var(--text); display: flex; align-items: center; padding: 15px; font-size: 17px; font-weight: 600; position: sticky; top: 0; z-index: 10; box-shadow: 0 1px 0 rgba(0,0,0,0.05); }
        .menu-icon { cursor: pointer; margin-right: 20px; color: var(--text); }
        .sidebar { position: fixed; top: 0; left: -260px; width: 260px; height: 100%; background: var(--surface); transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1); padding-top: 60px; z-index: 20; }
        .sidebar.active { transform: translateX(260px); }
        .sidebar a { display: flex; align-items: center; padding: 12px 20px; color: var(--text); text-decoration: none; font-size: 17px; position: relative; }
        .sidebar a .material-icons { margin-right: 15px; color: var(--secondary); }
        .sidebar a.active { background: rgba(0, 122, 255, 0.1); color: var(--primary); }
        .sidebar a.active .material-icons { color: var(--primary); }
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.5); opacity: 0; pointer-events: none; transition: opacity 0.3s; z-index: 15; }
        .overlay.active { opacity: 1; pointer-events: all; }
        .content { padding: 16px; z-index: 5; }
        .card { background: var(--surface); border-radius: 10px; padding: 16px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .card-title { font-size: 13px; font-weight: 500; color: var(--text-secondary); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
        .input-field { margin-bottom: 16px; }
        .input-field label { display: block; font-size: 13px; color: var(--text-secondary); margin-bottom: 4px; font-weight: 500; }
        select, input, textarea { width: 100%; padding: 12px 16px; font-size: 17px; border: 1px solid var(--border); border-radius: 10px; outline: none; background: var(--surface); -webkit-appearance: none; }
        select { background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%238E8E93'%3e%3cpath d='M7 10l5 5 5-5z'/%3e%3c/svg%3e"); background-repeat: no-repeat; background-position: right 16px center; background-size: 16px; }
        textarea { min-height: 100px; resize: vertical; }
        .btn { display: flex; align-items: center; justify-content: center; background: var(--primary); color: white; border: none; padding: 12px 16px; font-size: 17px; font-weight: 500; cursor: pointer; border-radius: 10px; position: relative; overflow: hidden; width: 100%; transition: background-color 0.2s; }
        .btn .material-icons { margin-right: 8px; }
        .btn:hover { background: #0062CC; }
        .btn:active { background: #004999; }
        .btn-outline { background: transparent; border: 1px solid var(--primary); color: var(--primary); }
        .btn-outline:hover { background: rgba(0, 122, 255, 0.1); }
        .btn-outline:active { background: rgba(0, 122, 255, 0.2); }
        .btn-danger { background: var(--danger); }
        .btn-danger:hover { background: #E63329; }
        .btn-danger:active { background: #CC2A20; }
        .ripple { position: absolute; border-radius: 50%; background-color: var(--ripple); transform: scale(0); animation: ripple 0.6s linear; pointer-events: none; }
        @keyframes ripple { to { transform: scale(4); opacity: 0; } }
        pre { background: var(--surface); padding: 16px; border-radius: 10px; white-space: pre-wrap; max-height: 300px; overflow-y: auto; font-family: 'SF Mono', Menlo, monospace; font-size: 13px; border: 1px solid var(--border); }
        .loading { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px 0; }
        .spinner { width: 24px; height: 24px; border: 3px solid rgba(0, 122, 255, 0.2); border-radius: 50%; border-top-color: var(--primary); animation: spin 1s ease-in-out infinite; margin-bottom: 16px; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .params-container { margin-top: 8px; }
        .param-row { display: flex; margin-bottom: 8px; align-items: center; }
        .param-row input { flex: 1; margin-right: 8px; padding: 8px 12px; font-size: 15px; }
        .param-row button { background: var(--danger); color: white; border: none; border-radius: 8px; padding: 8px 12px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .add-param { background: var(--primary) !important; color: #fff; margin-top: 8px; width: auto; padding: 8px 12px; font-size: 15px; }
        .settings-section { margin: 20px 0; padding: 16px; background: var(--surface); border-radius: 10px; border: 1px solid var(--border); }
        .settings-section h3 { margin-bottom: 12px; font-size: 16px; }
        .checkbox-container { display: flex; align-items: center; margin: 12px 0; }
        .checkbox-container input { width: auto; margin-right: 12px; transform: scale(1.2); }
        .switch { position: relative; display: inline-block; width: 52px; height: 32px; margin-right: 12px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 32px; }
        .slider:before { position: absolute; content: ""; height: 28px; width: 28px; left: 2px; bottom: 2px; background-color: white; transition: .4s; border-radius: 50%; }
        input:checked + .slider { background-color: var(--primary); }
        input:checked + .slider:before { transform: translateX(20px); }
        .response-info { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px; color: var(--text-secondary); }
        .status-success { color: var(--success); }
        .status-error { color: var(--danger); }
        .status-warning { color: var(--warning); }
        .history-item { padding: 12px 0; border-bottom: 1px solid var(--border); cursor: pointer; }
        .history-item:last-child { border-bottom: none; }
        .history-method { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; margin-right: 8px; background: var(--primary); color: white; }
        .history-url { font-size: 15px; margin-bottom: 4px; }
        .history-status { font-size: 12px; color: var(--text-secondary); }
        .empty-state { text-align: center; padding: 40px 0; color: var(--text-secondary); }
        .tab-bar { display: flex; background: var(--surface); border-radius: 10px; overflow: hidden; margin-bottom: 16px; }
        .tab { flex: 1; text-align: center; padding: 12px; font-size: 15px; font-weight: 500; cursor: pointer; transition: background-color 0.2s; }
        .tab.active { background: rgba(0, 122, 255, 0.1); color: var(--primary); }
        .response-tabs { margin-top: 16px; }
        .response-tab-content { display: none; }
        .response-tab-content.active { display: block; }
    </style>
</head>
<body>
    <div class="header">
        <span class="material-icons menu-icon" id="menuButton">menu</span>
        Starexx API Tester
    </div>
    <div class="overlay" id="overlay"></div>
    <div class="sidebar" id="sidebar">
        <a href="#" class="menu-item active" data-page="home">
            <span class="material-icons">home</span> Home
        </a>
        <a href="#" class="menu-item" data-page="response">
            <span class="material-icons">code</span> Response
        </a>
        <a href="#" class="menu-item" data-page="history">
            <span class="material-icons">history</span> History
        </a>
    </div>
    <div class="content">
        <div id="home" class="tab-content active">
            <div class="card">
                <div class="card-title">Request</div>
                <div class="input-field">
                    <label for="method">Method</label>
                    <select id="method">
                        <option value="GET">GET</option>
                        <option value="POST">POST</option>
                        <option value="PUT">PUT</option>
                        <option value="PATCH">PATCH</option>
                        <option value="DELETE">DELETE</option>
                        <option value="HEAD">HEAD</option>
                        <option value="OPTIONS">OPTIONS</option>
                    </select>
                </div>
                <div class="input-field">
                    <label for="url">URL</label>
                    <input type="text" id="url" placeholder="https://api.example.com/endpoint">
                </div>
            </div>
            <div class="card">
                <div class="card-title">Query Parameters</div>
                <div class="params-container" id="paramsContainer"></div>
                <button class="btn btn-outline add-param" id="addParamBtn">
                    <span class="material-icons">add</span> Add Parameter
                </button>
            </div>
            <div class="card">
                <div class="card-title">Headers</div>
                <div class="input-field">
                    <textarea id="headers" placeholder='{ "Content-Type": "application/json", "Authorization": "Bearer token" }'></textarea>
                </div>
            </div>
            <div class="card">
                <div class="card-title">Body</div>
                <div class="input-field">
                    <textarea id="body" placeholder='{ "key": "value" }'></textarea>
                </div>
            </div>
            <div class="card">
                <div class="card-title">Settings</div>
                <div class="checkbox-container">
                    <label class="switch">
                        <input type="checkbox" id="followRedirect" checked>
                        <span class="slider"></span>
                    </label>
                    <label for="followRedirect">Follow Redirects</label>
                </div>
                <div class="checkbox-container">
                    <label class="switch">
                        <input type="checkbox" id="includeCookies" checked>
                        <span class="slider"></span>
                    </label>
                    <label for="includeCookies">Include Cookies</label>
                </div>
                <div class="input-field">
                    <label for="timeout">Timeout (milliseconds)</label>
                    <input type="number" id="timeout" value="5000" min="0">
                </div>
            </div>
            <button class="btn" id="sendBtn">
                <span class="material-icons">send</span> Send Request
            </button>
        </div>
        <div id="response" class="tab-content">
            <div class="card">
                <div class="card-title">Response</div>
                <div id="loading" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    <p>Loading response...</p>
                </div>
                <div id="responseInfo" class="response-info" style="display: none;">
                    <span id="responseStatus">Status: 200 OK</span>
                    <span id="responseTime">Time: 250ms</span>
                </div>
                <div class="tab-bar response-tabs">
                    <div class="tab active" data-tab="pretty">Pretty</div>
                    <div class="tab" data-tab="raw">Raw</div>
                    <div class="tab" data-tab="headers">Headers</div>
                </div>
                <div class="response-tab-content active" id="prettyResponse">
                    <pre id="responseBox">Send a request to see the response here...</pre>
                </div>
                <div class="response-tab-content" id="rawResponse">
                    <pre id="rawResponseBox"></pre>
                </div>
                <div class="response-tab-content" id="headersResponse">
                    <pre id="headersResponseBox"></pre>
                </div>
            </div>
        </div>
        <div id="history" class="tab-content">
            <div class="card">
                <div class="card-title">History</div>
                <div id="historyList">
                    <div class="empty-state">No requests made yet</div>
                </div>
            </div>
        </div>
    </div>
    <script>
        const menuButton = document.getElementById('menuButton');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('overlay');
        const menuItems = document.querySelectorAll('.menu-item');
        const urlInput = document.getElementById('url');
        const paramsContainer = document.getElementById('paramsContainer');
        const addParamBtn = document.getElementById('addParamBtn');
        const sendBtn = document.getElementById('sendBtn');
        const historyList = document.getElementById('historyList');
        const responseTabs = document.querySelectorAll('.response-tabs .tab');

        document.addEventListener('DOMContentLoaded', function() {
            setupEventListeners();
            extractParamsFromURL();
            loadHistory();
        });

        function setupEventListeners() {
            menuButton.addEventListener('click', toggleMenu);
            overlay.addEventListener('click', toggleMenu);
            addParamBtn.addEventListener('click', addParamRow);
            sendBtn.addEventListener('click', handleSendRequest);
            
            menuItems.forEach(item => {
                item.addEventListener('click', function(e) {
                    e.preventDefault();
                    const page = this.getAttribute('data-page');
                    showPage(page);
                });
            });

            urlInput.addEventListener('change', extractParamsFromURL);
            urlInput.addEventListener('blur', extractParamsFromURL);

            responseTabs.forEach(tab => {
                tab.addEventListener('click', function() {
                    const tabName = this.getAttribute('data-tab');
                    switchResponseTab(tabName);
                });
            });
        }

        function toggleMenu() {
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        }

        function showPage(page) {
            document.querySelectorAll('.menu-item').forEach(item => {
                item.classList.remove('active');
            });
            document.querySelector(`.menu-item[data-page="${page}"]`).classList.add('active');
            
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.getElementById(page).classList.add('active');
        }

        function switchResponseTab(tabName) {
            responseTabs.forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelector(`.tab[data-tab="${tabName}"]`).classList.add('active');

            document.querySelectorAll('.response-tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.getElementById(`${tabName}Response`).classList.add('active');
        }

        function addParamRow(key = '', value = '') {
            const paramRow = document.createElement('div');
            paramRow.className = 'param-row';
            
            const keyInput = document.createElement('input');
            keyInput.type = 'text';
            keyInput.placeholder = 'Key';
            keyInput.value = key;
            
            const valueInput = document.createElement('input');
            valueInput.type = 'text';
            valueInput.placeholder = 'Value';
            valueInput.value = value;
            
            const removeBtn = document.createElement('button');
            removeBtn.innerHTML = '<span class="material-icons">delete</span>';
            removeBtn.addEventListener('click', function() {
                paramsContainer.removeChild(paramRow);
                updateURLWithParams();
            });
            
            const updateHandler = function() {
                updateURLWithParams();
            };
            
            keyInput.addEventListener('change', updateHandler);
            valueInput.addEventListener('change', updateHandler);
            
            paramRow.appendChild(keyInput);
            paramRow.appendChild(valueInput);
            paramRow.appendChild(removeBtn);
            
            paramsContainer.appendChild(paramRow);
        }

        function extractParamsFromURL() {
            const url = urlInput.value;
            if (!url) return;
            
            try {
                const urlObj = new URL(url);
                const params = new URLSearchParams(urlObj.search);
                
                paramsContainer.innerHTML = '';
                
                params.forEach((value, key) => {
                    addParamRow(key, value);
                });
                
                if (params.size === 0) {
                    addParamRow();
                }
            } catch (e) {}
        }

        function updateURLWithParams() {
            const url = urlInput.value;
            if (!url) return;
            
            try {
                const urlObj = new URL(url);
                const baseURL = urlObj.origin + urlObj.pathname;
                
                const params = [];
                document.querySelectorAll('.param-row').forEach(row => {
                    const key = row.querySelector('input[placeholder="Key"]').value;
                    const value = row.querySelector('input[placeholder="Value"]').value;
                    if (key) {
                        params.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`);
                    }
                });
                
                const newURL = baseURL + (params.length ? '?' + params.join('&') : '');
                urlInput.value = newURL;
            } catch (e) {}
        }

        function createRipple(event) {
            const button = event.currentTarget;
            const rect = button.getBoundingClientRect();
            
            const circle = document.createElement("span");
            const diameter = Math.max(button.clientWidth, button.clientHeight);
            const radius = diameter / 2;
            
            circle.style.width = circle.style.height = `${diameter}px`;
            circle.style.left = `${event.clientX - rect.left - radius}px`;
            circle.style.top = `${event.clientY - rect.top - radius}px`;
            circle.classList.add("ripple");
            
            const ripple = button.getElementsByClassName("ripple")[0];
            
            if (ripple) {
                ripple.remove();
            }
            
            button.appendChild(circle);
            
            setTimeout(() => {
                if (circle.parentNode === button) {
                    button.removeChild(circle);
                }
            }, 600);
        }

        function handleSendRequest(e) {
            createRipple(e);
            sendRequest();
        }

        function displayResponse(response) {
            document.getElementById('loading').style.display = 'none';
            
            const responseInfo = document.getElementById('responseInfo');
            const responseStatus = document.getElementById('responseStatus');
            const responseTimeEl = document.getElementById('responseTime');
            
            responseStatus.textContent = `Status: ${response.status} ${response.statusText}`;
            responseStatus.className = response.status >= 200 && response.status < 300 
                ? 'status-success' 
                : response.status >= 400 ? 'status-error' : 'status-warning';
            responseTimeEl.textContent = `Time: ${response.responseTime}`;
            responseInfo.style.display = 'flex';
            
            document.getElementById('responseBox').textContent = JSON.stringify(response.data, null, 2);
            document.getElementById('rawResponseBox').textContent = typeof response.data === 'string' 
                ? response.data 
                : JSON.stringify(response.data);
            document.getElementById('headersResponseBox').textContent = JSON.stringify(response.headers, null, 2);
            
            switchResponseTab('pretty');
        }

        function sendRequest() {
            const url = document.getElementById('url').value;
            const method = document.getElementById('method').value;
            const headersInput = document.getElementById('headers').value;
            const bodyInput = document.getElementById('body').value;
            const followRedirect = document.getElementById('followRedirect').checked;
            const includeCookies = document.getElementById('includeCookies').checked;
            const timeout = parseInt(document.getElementById('timeout').value);

            if (!url) {
                alert("Please enter a URL");
                return;
            }

            showPage('response');
            document.getElementById('loading').style.display = 'flex';
            document.getElementById('responseInfo').style.display = 'none';
            document.getElementById('responseBox').textContent = '';

            let headers = {};
            try {
                headers = headersInput ? JSON.parse(headersInput) : {};
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('responseBox').textContent = "Error: Invalid Headers JSON - " + error.message;
                return;
            }

            const requestData = {
                url,
                method,
                headers,
                body: bodyInput,
                followRedirect,
                includeCookies,
                timeout
            };

            fetch('/send-request', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    displayResponse({
                        status: 0,
                        statusText: 'Error',
                        responseTime: '0 ms',
                        headers: {},
                        data: { error: data.error }
                    });
                } else {
                    displayResponse(data.response);
                    loadHistory();
                }
            })
            .catch(error => {
                displayResponse({
                    status: 0,
                    statusText: 'Error',
                    responseTime: '0 ms',
                    headers: {},
                    data: { error: error.message }
                });
            });
        }

        function loadHistory() {
            fetch('/get-history')
                .then(res => res.json())
                .then(history => {
                    if (history.length === 0) {
                        historyList.innerHTML = '<div class="empty-state">No requests made yet</div>';
                        return;
                    }
                    
                    let html = '';
                    history.forEach((item, index) => {
                        const statusClass = item.response.status >= 200 && item.response.status < 300 
                            ? 'status-success' 
                            : item.response.status >= 400 ? 'status-error' : 'status-warning';
                        
                        html += `
                        <div class="history-item" data-index="${index}">
                            <div class="history-url">
                                <span class="history-method">${item.request.method}</span>
                                ${item.request.url}
                            </div>
                            <div class="history-status">
                                <span class="${statusClass}">${item.response.status} ${item.response.statusText}</span>
                                • ${item.response.responseTime}
                                • ${new Date(item.timestamp).toLocaleString()}
                            </div>
                        </div>
                        `;
                    });
                    
                    historyList.innerHTML = html;
                    
                    document.querySelectorAll('.history-item').forEach(item => {
                        item.addEventListener('click', function() {
                            loadHistoryItem(parseInt(this.getAttribute('data-index')));
                        });
                    });
                });
        }

        function loadHistoryItem(index) {
            fetch('/get-history')
                .then(res => res.json())
                .then(history => {
                    if (index < 0 || index >= history.length) return;
                    
                    const item = history[index];
                    
                    document.getElementById('method').value = item.request.method;
                    document.getElementById('url').value = item.request.url;
                    
                    try {
                        const urlObj = new URL(item.request.url);
                        const params = new URLSearchParams(urlObj.search);
                        
                        paramsContainer.innerHTML = '';
                        
                        params.forEach((value, key) => {
                            addParamRow(key, value);
                        });
                        
                        if (params.size === 0) {
                            addParamRow();
                        }
                    } catch (e) {}
                    
                    document.getElementById('headers').value = JSON.stringify(item.request.headers, null, 2);
                    document.getElementById('body').value = item.request.body || '';
                    
                    showPage('response');
                    displayResponse(item.response);
                });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

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
        if not os.path.exists('history.json'):
            with open('history.json', 'w') as f:
                json.dump([], f)
        
        with open('history.json', 'r') as f:
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
        if os.path.exists('history.json'):
            with open('history.json', 'r') as f:
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
        
        with open('history.json', 'w') as f:
            json.dump(history, f, indent=2)
            
    except Exception as e:
        print(f"Error saving history: {str(e)}")

if __name__ == '__main__':
    if not os.path.exists('history.json'):
        with open('history.json', 'w') as f:
            json.dump([], f)
    app.run(debug=True)