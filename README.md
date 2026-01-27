# Onebby API

A comprehensive e-commerce REST API built with FastAPI and PostgreSQL, designed for high-performance product and category management.

---

## Project Overview

Onebby API is a robust backend system that provides complete e-commerce functionality including product management, category hierarchies, brand and tax handling, discount campaigns, and secure API key authentication.

---

## Technology Stack

**Framework & Language**
- Python 3.9+
- FastAPI - High-performance web framework

**Database & ORM**
- PostgreSQL 12+
- SQLAlchemy - SQL toolkit and ORM
- Alembic - Database migration tool

**Authentication & Security**
- API Key authentication
- JWT token support
- Secure password hashing

**Data Validation**
- Pydantic - Data validation using Python type hints

---

## Project Structure

```
onebby-api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── categories.py       # Category management endpoints
│   │       ├── products.py         # Product CRUD operations
│   │       ├── brands_taxes.py     # Brand and tax management
│   │       ├── discounts.py        # Discount campaign handling
│   │       ├── users.py            # User management
│   │       ├── upload.py           # File upload handling
│   │       └── import_products.py  # Bulk product import
│   ├── core/
│   │   ├── config.py               # Application configuration
│   │   ├── security/               # Authentication and authorization
│   │   ├── exceptions.py           # Custom exception definitions
│   │   └── logging_config.py       # Logging configuration
│   ├── crud/
│   │   ├── category.py             # Category database operations
│   │   ├── product.py              # Product database operations
│   │   ├── user.py                 # User database operations
│   │   └── discount_campaign.py    # Discount operations
│   ├── models/
│   │   ├── category.py             # Category data model
│   │   ├── product.py              # Product data model
│   │   ├── brand.py                # Brand data model
│   │   ├── user.py                 # User data model
│   │   └── discount_campaign.py    # Discount campaign model
│   ├── schemas/
│   │   ├── category.py             # Category request/response schemas
│   │   ├── product.py              # Product schemas
│   │   └── discount_campaign.py    # Discount schemas
│   ├── services/
│   │   ├── product_import.py       # Product import service
│   │   └── product_enrichment.py   # Product data enrichment
│   └── db/
│       └── session.py              # Database session management
├── alembic/                        # Database migrations
├── tests/                          # Test suites
├── main.py                         # Application entry point
└── requirements.txt                # Python dependencies
```

---

## Installation & Setup

### Prerequisites

- Python 3.9 or higher
- PostgreSQL 12 or higher
- pip package manager

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd onebby-api
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/macOS
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Database Configuration

Create a PostgreSQL database:

```bash
psql -U postgres
CREATE DATABASE onebby_db;
CREATE USER onebby_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE onebby_db TO onebby_user;
\q
```

### Step 5: Environment Configuration

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://onebby_user:your_password@localhost:5432/onebby_db
API_V1_STR=/api/v1
PROJECT_NAME=Onebby API
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Step 6: Run Database Migrations

```bash
alembic upgrade head
```

### Step 7: Start Application

```bash
# Development mode
python main.py

# Or using uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

---

## API Documentation

Interactive API documentation is automatically generated:

- **Swagger UI**: `http://localhost:8000/api/v1/docs`
- **ReDoc**: `http://localhost:8000/api/v1/redoc`
- **OpenAPI Spec**: `http://localhost:8000/api/v1/openapi.json`

---

## Core Features

### Category Management
- Hierarchical category structure (parent-child relationships)
- Category translations support
- CRUD operations for categories
- Category tree navigation

### Product Management
- Complete product lifecycle management
- Product variants support
- Image and file handling
- Bulk product import from Excel
- Product categorization
- Brand and tax class assignment

### Discount Campaigns
- Create and manage discount campaigns
- Apply discounts to specific products
- Time-based campaign activation

### Brand & Tax Management
- Brand catalog management
- Tax class configuration
- Link brands to tax classes

### User Management
- User authentication and authorization
- Role-based access control
- Secure API key generation

---

## API Endpoints

### Health Check
```
GET /api/v1/health
```

### Categories
```
GET    /api/v1/categories              # List all categories
GET    /api/v1/categories/{id}         # Get category details
POST   /api/v1/categories              # Create category
PUT    /api/v1/categories/{id}         # Update category
DELETE /api/v1/categories/{id}         # Delete category
```

### Products
```
GET    /api/v1/products                # List products
GET    /api/v1/products/{id}           # Get product details
POST   /api/v1/products                # Create product
PUT    /api/v1/products/{id}           # Update product
DELETE /api/v1/products/{id}           # Delete product
POST   /api/v1/products/import         # Bulk import products
```

### Brands & Taxes
```
GET    /api/v1/brands                  # List brands
POST   /api/v1/brands                  # Create brand
GET    /api/v1/tax-classes             # List tax classes
```

### Discounts
```
GET    /api/v1/discounts               # List discount campaigns
POST   /api/v1/discounts               # Create discount campaign
PUT    /api/v1/discounts/{id}          # Update campaign
DELETE /api/v1/discounts/{id}          # Delete campaign
```

---

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

---

## Development Guidelines

### Code Standards
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and returns
- Document complex logic with inline comments
- Keep functions focused and modular

### Database Operations
- Use SQLAlchemy ORM for all database operations
- Implement proper transaction handling
- Use database migrations for schema changes

### API Design
- RESTful endpoint conventions
- Proper HTTP status codes
- Consistent error responses
- Pagination for list endpoints

---

## Testing

Run test suite:
```bash
pytest

# With coverage report
pytest --cov=app --cov-report=html
```

---

## Production Deployment

### Configuration
- Set `DEBUG=False` in production
- Use strong `SECRET_KEY`
- Enable HTTPS
- Configure CORS properly
- Set appropriate database connection pool size

### Server Recommendations
- Use Gunicorn with Uvicorn workers
- Configure reverse proxy (Nginx)
- Implement rate limiting
- Set up database backups
- Enable monitoring and logging

---

## Security Considerations

- All endpoints require API key authentication
- Passwords are hashed using secure algorithms
- SQL injection protection via SQLAlchemy ORM
- Input validation using Pydantic schemas
- CORS configuration for frontend integration

---

## Author

Muthana

---

## Copyright

Copyright 2026 Muthana. All rights reserved.
Unauthorized copying or distribution is prohibited.

---

## Support

For technical support or inquiries, please contact the development team.
