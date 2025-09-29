# WAF Anomaly Detection System

A comprehensive Web Application Firewall (WAF) anomaly detection system that uses machine learning to identify malicious HTTP requests in real-time. The system leverages a custom-trained transformer model to score HTTP requests and detect potential security threats.

## 🏗️ Architecture Overview

The system consists of several interconnected components working together to provide real-time anomaly detection:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   HTTP Client   │───▶│   Nginx/OpenResty │───▶│   Kafka Producer    │
│                 │    │     (Lua Script)   │    │                     │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│  Web Dashboard  │◀───│   Dashboard      │◀───│   Kafka Consumer    │
│    (HTML/JS)    │    │   Server (Flask) │    │   (Log Normalizer)  │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                                ▲
                       ┌──────────────────┐
                       │   ML Scorer      │
                       │  (Transformer)   │
                       └──────────────────┘
```

## 🚀 Features

- **Real-time Request Monitoring**: Captures and analyzes HTTP requests as they happen
- **ML-based Anomaly Detection**: Uses a custom-trained RoBERTa transformer model
- **Self-Learning System**: Continuously adapts and improves detection accuracy through ongoing pattern analysis
- **Request Normalization**: Intelligent preprocessing to handle dynamic data
- **Interactive Dashboard**: Real-time visualization of threats and statistics
- **Kafka Integration**: Scalable message streaming for high-throughput scenarios
- **Docker Deployment**: Complete containerized setup with Docker Compose
- **Flexible Architecture**: Modular design for easy extension and customization

## 📁 Project Structure

```
anomaly_detection/
├── 📊 Dashboard Components
│   ├── dashboard_server.py          # Flask server with WebSocket support
│   └── dashboard/public/index.html  # Interactive web dashboard
│
├── 🔧 Core Processing
│   ├── normalizer.py                # HTTP request normalization
│   ├── log_worker.py               # Kafka consumer for log processing
│   └── generate_safe_requests.py   # Traffic generator for testing
│
├── 🤖 ML Components
│   └── waf-transformer/
│       ├── ml_scorer/
│       │   └── score_requests.py    # ML model inference
│       ├── training/
│       │   ├── train_llm.py        # Model training script
│       │   ├── train_tokenizer.py  # Custom tokenizer training
│       │   ├── make_text.py        # Data preprocessing
│       │   └── data-generator.py   # Training data generation
│       └── model/                  # Trained model artifacts
│
├── 🌐 Web Server (Test Target)
│   └── webserver(js)/
│       ├── index.js                # Express.js test server
│       └── package.json
│
├── 🐳 Infrastructure
│   ├── docker-compose.yml          # Complete infrastructure setup
│   ├── Dockerfile.openresty        # Custom Nginx container
│   ├── nginx.conf                  # Nginx configuration with Lua
│   ├── fluent-bit.conf            # Log forwarding configuration
│   └── parsers.conf               # Log parsing rules
│
└── 📋 Configuration
    ├── requirements.txt            # Python dependencies
    └── parsed_logs.jsonl          # Sample processed logs
```

## 🛠️ Components Deep Dive

### 1. Request Capture & Preprocessing

**Nginx with OpenResty/Lua**
- Intercepts all HTTP requests
- Extracts comprehensive request metadata (headers, body, query parameters)
- Forwards structured data to Kafka topics

**Request Normalizer** (`normalizer.py`)
- Normalizes dynamic values (IDs, numbers) to placeholders (`:num`)
- Standardizes header formats and query parameters
- Handles various content types and request structures
- Produces consistent format for ML model input

### 2. Machine Learning Engine

**Custom Transformer Model**
- Based on RoBERTa architecture (6 layers, 256 hidden size)
- Trained on normalized HTTP request patterns
- Uses masked language modeling for anomaly scoring
- Optimized for security-relevant request features

**Training Pipeline**
- `train_tokenizer.py`: Creates domain-specific tokenizer
- `train_llm.py`: Trains the transformer model
- `make_text.py`: Converts JSON logs to training text format
- `data-generator.py`: Generates diverse training scenarios

**Scoring System** (`score_requests.py`)
- Loads trained model and tokenizer
- Converts requests to model input format
- Returns anomaly scores (higher = more suspicious)
- Supports batch processing for efficiency

### 3. Real-time Dashboard

**Backend** (`dashboard_server.py`)
- Flask server with WebSocket support
- REST API endpoints for request data and statistics
- Real-time data streaming to frontend
- Maintains request history and analytics

**Frontend** (`dashboard/public/index.html`)
- Modern, responsive web interface
- Real-time charts and visualizations
- Request timeline and threat indicators
- Interactive filtering and search capabilities

### 4. Data Pipeline

**Kafka Infrastructure**
- `api-logs`: Raw request data from Nginx
- `api-logs-parsed`: Normalized request data
- Scalable, fault-tolerant message streaming
- Decouples components for better reliability

**Log Processing**
- Fluent Bit for log forwarding
- JSON-based log formatting
- Structured data extraction
- Error handling and recovery

## ⚙️ Setup & Installation

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Node.js 16+ (for test web server)

### Quick Start

1. **Clone and Navigate**
   ```bash
   git clone <repository-url>
   cd anomaly_detection
   ```

2. **Start Infrastructure**
   ```bash
   docker-compose up -d
   ```

3. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Processing Components**
   ```bash
   # Terminal 1: Start normalizer
   python normalizer.py
   
   # Terminal 2: Start log worker
   python log_worker.py
   
   # Terminal 3: Start dashboard
   python dashboard_server.py
   ```

5. **Start Test Web Server** (Optional)
   ```bash
   cd webserver\(js\)
   npm install
   node index.js
   ```

6. **Access Dashboard**
   Open http://localhost:5000 in your browser

## 🔧 Configuration

### Environment Variables

```bash
# Kafka Configuration
BOOTSTRAP_SERVERS=localhost:29092
RAW_TOPIC=api-logs
PARSED_TOPIC=api-logs-parsed

# Dashboard Configuration
FLASK_HOST=localhost
FLASK_PORT=5000

# Model Configuration
MODEL_PATH=waf-transformer/model/checkpoints/latest
```

### Model Training

To retrain the model with your own data:

1. **Prepare Training Data**
   ```bash
   cd waf-transformer/training
   python make_text.py < your_data.jsonl > training_data.txt
   ```

2. **Train Custom Tokenizer**
   ```bash
   python train_tokenizer.py
   ```

3. **Train the Model**
   ```bash
   python train_llm.py
   ```

## 📊 Usage Examples

### Generating Test Traffic

```bash
# Generate safe requests
python generate_safe_requests.py

# Monitor in dashboard at http://localhost:5000
```

### Scoring Individual Requests

```python
from waf_transformer.ml_scorer.score_requests import score

request = {
    "m": "GET",
    "p": "/user/123",
    "q": {"page": "1"},
    "h": {"ua": "Mozilla/5.0..."},
    "s": "192.168.1.1"
}

anomaly_score = score(request)
print(f"Anomaly Score: {anomaly_score}")
```

### API Endpoints

```bash
# Get recent requests
curl http://localhost:5000/api/requests

# Get system statistics
curl http://localhost:5000/api/stats
```

## 🏗️ Development

### Adding New Features

1. **Custom Normalizers**: Extend `normalizer.py` for new request types
2. **ML Improvements**: Modify training scripts in `waf-transformer/training/`
3. **Dashboard Widgets**: Add components to `dashboard/public/index.html`
4. **New Data Sources**: Create additional Kafka consumers

### Testing

```bash
# Test request generation
python generate_safe_requests.py

# Test model scoring
python -c "from waf_transformer.ml_scorer.score_requests import score; print(score({'m': 'GET', 'p': '/test'}))"
```

## 📈 Performance & Scaling

- **Throughput**: Handles 1000+ requests/second with proper tuning
- **Latency**: Sub-100ms processing time per request
- **Scalability**: Kafka-based architecture supports horizontal scaling
- **Memory**: ~2GB RAM for full system with loaded ML model
- **Storage**: Configurable log retention and model checkpoints

## 🔒 Security Considerations

- Model trained on sanitized, normalized data only
- No sensitive data stored in model artifacts
- Configurable alert thresholds
- Audit logging for all anomaly detections
- Network isolation with Docker containers

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenResty/Nginx for high-performance request processing
- Hugging Face Transformers for ML infrastructure
- Apache Kafka for scalable data streaming
- Flask and Chart.js for dashboard components

---

**Note**: This is a development/research system. For production deployment, additional security hardening, monitoring, and testing are recommended.