# Insurance Document Validator API

A FastAPI application that uses Groq AI to extract and validate data from insurance documents.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Quick Start

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Get your Groq API key from [console.groq.com/keys](https://console.groq.com/keys) and add it to `.env`:

```bash
cp .env.example .env
# Edit .env and add: GROQ_API_KEY=your_actual_key_here
```

### Run

```bash
# Start the server
python run.py

# Or with uvicorn
uvicorn app.main:app --reload
```

Visit: http://localhost:8000/docs

## API Endpoints

- `POST /api/v1/validate` - Validate insurance documents
- `GET /health` - Health check
- `GET /` - API info
- `GET /docs` - Interactive API documentation

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## Docker

```bash
# Build and run
docker-compose up -d

# Or manually
docker build -t insurance-validator .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key insurance-validator
```

## Project Structure

```
genoshi-backend/
├── app/                    # Application code
│   ├── api/               # API endpoints
│   ├── core/              # Configuration
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   └── utils/             # Utilities
├── tests/                 # Test suite
├── data/                  # Data files
├── run.py                 # App runner
└── requirements.txt       # Dependencies
```

## Configuration

Environment variables in `.env`:

- `GROQ_API_KEY` - Your Groq API key (required)
- `APP_HOST` - Server host (default: 0.0.0.0)
- `APP_PORT` - Server port (default: 8000)

## Example Usage

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/validate",
    json={
        "document_text": """
        Policy Number: HM-2025-10-A4B
        Vessel: MV Neptune
        Start Date: 2025-11-01
        End Date: 2026-10-31
        Insured Value: $5,000,000
        """
    }
)

print(response.json())
```

## Features

- AI-powered document extraction using Groq/Llama
- Automatic validation rules
- RESTful API with OpenAPI documentation
- Docker support
- Comprehensive test suite
- Production-ready

## License

MIT License
