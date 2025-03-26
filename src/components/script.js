// DOM Elements
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

// Initialize the app
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

    // Auto-detect URL changes to extract parameters
    urlInput.addEventListener('change', extractParamsFromURL);
    urlInput.addEventListener('blur', extractParamsFromURL);

    // Response tabs
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
    // Update active menu item
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`.menu-item[data-page="${page}"]`).classList.add('active');
    
    // Show the selected page
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.getElementById(page).classList.add('active');
}

function switchResponseTab(tabName) {
    // Update active tab
    responseTabs.forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`.tab[data-tab="${tabName}"]`).classList.add('active');

    // Show the selected tab content
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
    
    // Update URL when params change
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
        
        // Clear existing params
        paramsContainer.innerHTML = '';
        
        // Add params from URL
        params.forEach((value, key) => {
            addParamRow(key, value);
        });
        
        // Add one empty row if no params found
        if (params.size === 0) {
            addParamRow();
        }
    } catch (e) {
        // Not a valid URL, ignore
    }
}

function updateURLWithParams() {
    const url = urlInput.value;
    if (!url) return;
    
    try {
        const urlObj = new URL(url);
        const baseURL = urlObj.origin + urlObj.pathname;
        
        // Build new query string
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
    } catch (e) {
        // Not a valid URL, ignore
    }
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
    
    // Remove ripple element after animation completes
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

function loadHistory() {
    fetch('/api/history')
        .then(response => response.json())
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
                        <span class="${statusClass}">${item.response.status} ${item.response.statusText || ''}</span>
                        • ${Math.round(item.response.responseTime)}ms
                        • ${new Date(item.timestamp).toLocaleString()}
                    </div>
                </div>
                `;
            });
            
            historyList.innerHTML = html;
            
            // Add click handlers to history items
            document.querySelectorAll('.history-item').forEach(item => {
                item.addEventListener('click', function() {
                    loadHistoryItem(parseInt(this.getAttribute('data-index')));
                });
            });
        })
        .catch(error => {
            console.error('Error loading history:', error);
            historyList.innerHTML = '<div class="empty-state">Error loading history</div>';
        });
}

function loadHistoryItem(index) {
    fetch('/api/history')
        .then(response => response.json())
        .then(history => {
            if (index < 0 || index >= history.length) return;
            
            const item = history[index];
            
            // Update request fields
            document.getElementById('method').value = item.request.method;
            document.getElementById('url').value = item.request.url;
            
            // Update parameters
            try {
                const urlObj = new URL(item.request.url);
                const params = new URLSearchParams(urlObj.search);
                
                // Clear existing params
                paramsContainer.innerHTML = '';
                
                // Add params from URL
                params.forEach((value, key) => {
                    addParamRow(key, value);
                });
                
                // Add one empty row if no params found
                if (params.size === 0) {
                    addParamRow();
                }
            } catch (e) {
                // Not a valid URL, ignore
            }
            
            // Update headers and body
            document.getElementById('headers').value = JSON.stringify(item.request.headers, null, 2);
            document.getElementById('body').value = item.request.body || '';
            document.getElementById('timeout').value = item.request.timeout || 5000;
            document.getElementById('followRedirect').checked = item.request.follow_redirects;
            document.getElementById('includeCookies').checked = item.request.include_cookies;
            
            // Switch to response tab and show the response
            showPage('response');
            displayResponse(item.response);
        });
}

function displayResponse(response) {
    document.getElementById('loading').style.display = 'none';
    
    const responseInfo = document.getElementById('responseInfo');
    const responseStatus = document.getElementById('responseStatus');
    const responseTimeEl = document.getElementById('responseTime');
    
    responseStatus.textContent = `Status: ${response.status} ${response.status_text || ''}`;
    responseStatus.className = response.status >= 200 && response.status < 300 
        ? 'status-success' 
        : response.status >= 400 ? 'status-error' : 'status-warning';
    responseTimeEl.textContent = `Time: ${Math.round(response.response_time)}ms`;
    responseInfo.style.display = 'flex';
    
    // Pretty JSON
    try {
        const prettyJson = typeof response.body === 'string' 
            ? JSON.parse(response.body) 
            : response.body;
        document.getElementById('responseBox').textContent = JSON.stringify(prettyJson, null, 2);
    } catch (e) {
        document.getElementById('responseBox').textContent = response.body;
    }
    
    // Raw response
    document.getElementById('rawResponseBox').textContent = typeof response.body === 'string' 
        ? response.body 
        : JSON.stringify(response.body);
    
    // Headers
    document.getElementById('headersResponseBox').textContent = JSON.stringify(response.headers, null, 2);
    
    // Switch to pretty tab by default
    switchResponseTab('pretty');
}

async function sendRequest() {
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

    // Show loading and switch to response tab
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
        method: method,
        url: url,
        headers: headers,
        body: bodyInput,
        timeout: timeout,
        follow_redirects: followRedirect,
        include_cookies: includeCookies
    };

    try {
        const response = await fetch('/api/proxy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        // Display the response
        displayResponse(data);
        
    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        const responseInfo = document.getElementById('responseInfo');
        const responseStatus = document.getElementById('responseStatus');
        
        responseStatus.textContent = `Error: ${error.message}`;
        responseStatus.className = 'status-error';
        responseInfo.style.display = 'flex';
        
        document.getElementById('responseBox').textContent = error.stack || error.message;
    }
                                            }
