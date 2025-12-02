# 🚀 Onebby API

FastAPI-based REST API with PostgreSQL database.

## 📁 Project Structure

```
onebby-api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py          # API router
│   │       └── health.py       # Health check endpoint
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py           # Configuration settings
│   ├── db/
│   │   ├── __init__.py
│   │   └── session.py          # Database session
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py             # Base model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── health.py           # Pydantic schemas
│   └── __init__.py
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
├── .env.example                 # Example environment file
└── .gitignore                   # Git ignore rules
```

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.9+
- PostgreSQL 12+

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE onebby_db;
\q
```

### 4. Configure Environment

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Edit `.env` and update database credentials:
```
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/onebby_db
```

### 5. Run the Application

```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📖 API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## 🔗 Available Endpoints

### Root
- `GET /` - Welcome message and API information

### Health Check
- `GET /api/v1/health` - API health status and database connectivity

Example response:
```json
{
  "status": "healthy",
  "message": "Onebby API is running",
  "timestamp": "2025-12-02T10:30:00.000Z",
  "database": "connected"
}
```

## 🔮 Coming Soon

- ✨ JWT Authentication
- 📝 CRUD Operations
- 📤 File Upload Support
- 🔒 Advanced Security Features

## 🧪 Testing

```bash
# Run tests (coming soon)
pytest
```

## 📝 Development Notes

- The API uses FastAPI for high performance
- SQLAlchemy ORM for database operations
- Pydantic for data validation
- Automatic API documentation generation

## 🤝 Contributing

This is a private project. For questions, contact the development team.

## 📄 License

Private - All rights reserved
