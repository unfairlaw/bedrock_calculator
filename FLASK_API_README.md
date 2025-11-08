# AWS Cost Agent - Flask Web API

A beautiful web interface for the AWS Cost Agent with REST API endpoints.

## 🌟 Features

- **Modern Web UI** - Clean, responsive interface
- **Natural Language** - Ask cost questions in plain English
- **Real-time Estimation** - Get instant cost breakdowns
- **Multiple Calculators** - Automatically routes to RAG, Compute, or Abstract calculator
- **REST API** - Full API for programmatic access
- **Session Management** - Maintains conversation history

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python3 app.py
```

The server will start on `http://localhost:5000`

### 3. Open in Browser

Navigate to `http://localhost:5000` in your web browser.

## 📡 API Endpoints

### GET /
Serves the web interface.

### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-08T...",
  "version": "1.0.0"
}
```

### POST /api/estimate
Main cost estimation endpoint.

**Request:**
```json
{
  "query": "How much for 10 t3.medium instances?",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "success": true,
  "message": "📊 Compute & Storage Cost Estimate\n...",
  "data": null,
  "tool_used": "compute_calculator",
  "timestamp": "2025-11-08T..."
}
```

### GET /api/tools
Get available calculator tools.

**Response:**
```json
{
  "tools": [
    {
      "id": "rag_calculator",
      "name": "RAG Cost Calculator",
      "description": "...",
      "keywords": ["rag", "bedrock", ...],
      "example": "..."
    },
    ...
  ]
}
```

### GET /api/examples
Get example queries.

**Response:**
```json
{
  "examples": [
    {
      "category": "RAG Systems",
      "icon": "🤖",
      "queries": [...]
    },
    ...
  ]
}
```

### GET /api/session/history
Get conversation history for a session.

**Query Parameters:**
- `session_id` (optional): Session ID

**Response:**
```json
{
  "success": true,
  "history": [
    {
      "role": "user",
      "content": "..."
    },
    {
      "role": "assistant",
      "content": "..."
    }
  ]
}
```

### POST /api/session/clear
Clear conversation session.

**Request:**
```json
{
  "session_id": "session-id"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Session cleared"
}
```

## 🎨 Web Interface

### Features

- **Chat Interface** - Conversational UI like ChatGPT
- **Example Queries** - One-click example questions
- **Tool Information** - See available calculators
- **Responsive Design** - Works on desktop and mobile
- **Syntax Highlighting** - Color-coded cost breakdowns

### Screenshots

```
┌─────────────────────────────────────────────────────┐
│  🤖 AWS Cost Agent                                  │
│  AI-powered AWS cost estimation in natural language │
├─────────────────────────────────────────────────────┤
│  💡 Examples  │  Chat Area                          │
│  🛠️  Tools     │  ┌──────────────────────────────┐ │
│  🗑️  Clear     │  │ You: How much for 10 EC2?   │ │
│                │  │                              │ │
│                │  │ Agent: $140/month           │ │
│                │  └──────────────────────────────┘ │
│                │  [Type your question...]         │
└─────────────────────────────────────────────────────┘
```

## 💻 Development

### Project Structure

```
bedrock_calculator/
├── app.py                      # Flask application
├── templates/
│   └── index.html             # HTML template
├── static/
│   ├── css/
│   │   └── style.css          # Stylesheets
│   └── js/
│       └── app.js             # JavaScript client
├── requirements.txt            # Python dependencies
└── FLASK_API_README.md        # This file
```

### Running in Development Mode

```bash
# Enable debug mode (auto-reload on changes)
export FLASK_ENV=development
python3 app.py
```

### Customization

#### Change Port

Edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8000)  # Change port to 8000
```

#### Add CORS Domains

Edit `app.py`:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "https://yourdomain.com"]
    }
})
```

#### Customize Styling

Edit `static/css/style.css`:
```css
:root {
    --primary-color: #your-color;
    /* ... */
}
```

## 🚢 Production Deployment

### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t aws-cost-agent .
docker run -p 5000:5000 aws-cost-agent
```

### Using Nginx + Gunicorn

1. Run Gunicorn on localhost:
```bash
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

2. Configure Nginx (`/etc/nginx/sites-available/cost-agent`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/bedrock_calculator/static;
    }
}
```

3. Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/cost-agent /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### Environment Variables

```bash
# Production settings
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here

# Custom port
export PORT=8080

# Run
python3 app.py
```

## 🧪 Testing

### Test API Endpoints

```bash
# Health check
curl http://localhost:5000/api/health

# Cost estimation
curl -X POST http://localhost:5000/api/estimate \
  -H "Content-Type: application/json" \
  -d '{"query": "How much for 10 t3.medium instances?"}'

# Get tools
curl http://localhost:5000/api/tools

# Get examples
curl http://localhost:5000/api/examples
```

### Load Testing

Using Apache Bench:
```bash
ab -n 1000 -c 10 http://localhost:5000/api/health
```

## 🔒 Security Considerations

### Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS with SSL/TLS certificates
- [ ] Implement rate limiting
- [ ] Add authentication if needed
- [ ] Sanitize user inputs
- [ ] Use a production WSGI server (Gunicorn)
- [ ] Set up proper logging
- [ ] Configure CORS appropriately
- [ ] Use a reverse proxy (Nginx)

### Rate Limiting

Add Flask-Limiter:
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per hour"]
)

@app.route('/api/estimate', methods=['POST'])
@limiter.limit("20 per minute")
def estimate():
    # ...
```

### Authentication

Add basic auth:
```python
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    # Verify credentials
    return username == "admin" and password == "secret"

@app.route('/api/estimate', methods=['POST'])
@auth.login_required
def estimate():
    # ...
```

## 📊 Monitoring

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.route('/api/estimate', methods=['POST'])
def estimate():
    logger.info(f"Estimation request: {request.get_json()}")
    # ...
```

### Metrics

Track API usage:
```python
from collections import defaultdict

metrics = defaultdict(int)

@app.route('/api/estimate', methods=['POST'])
def estimate():
    metrics['total_requests'] += 1
    # ...

@app.route('/api/metrics')
def get_metrics():
    return jsonify(dict(metrics))
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>
```

### Module Not Found

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # On Linux/Mac
venv\Scripts\activate     # On Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### CORS Errors

Add to `app.py`:
```python
from flask_cors import CORS
CORS(app)  # Enable CORS for all routes
```

### Static Files Not Loading

Check paths in `app.py`:
```python
app = Flask(__name__,
            static_folder='static',
            template_folder='templates')
```

## 🔗 Integration Examples

### cURL

```bash
curl -X POST http://localhost:5000/api/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Estimate RAG costs for 100 manuals",
    "session_id": "my-session"
  }'
```

### Python Requests

```python
import requests

response = requests.post('http://localhost:5000/api/estimate', json={
    'query': 'How much for 10 t3.medium instances?',
    'session_id': 'my-session'
})

data = response.json()
print(data['message'])
```

### JavaScript Fetch

```javascript
fetch('http://localhost:5000/api/estimate', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        query: 'How much for 10 t3.medium instances?',
        session_id: 'my-session'
    })
})
.then(res => res.json())
.then(data => console.log(data.message));
```

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [AWS Cost Calculator Suite README](README.md)
- [Agent Documentation](AGENT_README.md)

## 🤝 Contributing

To add new API endpoints:

1. Add route in `app.py`
2. Update frontend in `static/js/app.js`
3. Update this documentation

## 📄 License

MIT License - Same as parent project

---

**Built with Flask and ❤️**

For questions or issues, please refer to the main [README.md](README.md)
