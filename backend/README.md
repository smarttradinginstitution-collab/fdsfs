# Trade Vantage - Backend API

This is the core backend API for the Trade Vantage platform. Built with **FastAPI**, it serves as the central nervous system for data processing, analytics, and data persistence. It adheres to a strict **Clean Architecture** pattern to ensure scalability, maintainability, and testability.

## 🏗️ Architecture & Design Patterns

The backend is structured into distinct layers, each with a specific responsibility. Data flows from the outer layers (API) inwards to the core business logic and data access.

### 1. Presentation Layer (Routers & Controllers)
- **Routers (`app/Router/`)**: Define the HTTP endpoints, handle dependency injection (FastAPI `Depends`), and route requests to the appropriate controllers. They also enforce authentication and authorization scopes.
- **Controllers (`app/Controllers/`)**: The entry point for application logic. They receive Pydantic schemas, perform initial validation, and call the appropriate Service methods. They are responsible for formatting the HTTP response.

### 2. Business Logic Layer (Services)
- **Services (`app/Services/`)**: Contain the core business rules and use cases. This is where the "magic" happens.
    - **SOA Service**: Handles complex statistical analysis using Pandas and Scikit-learn.
    - **Parsers**: Dedicated services for parsing trade files from NinjaTrader, MT5, etc.
    - **Orchestrators**: Services that coordinate multiple repositories (e.g., `ImportService` managing file uploads, parsing, and database insertion).

### 3. Data Access Layer (Repositories)
- **Repositories (`app/Repositories/`)**: Abstract the database interactions. They use **SQLAlchemy (Async)** to perform CRUD operations. This isolation allows us to swap the underlying database or optimize queries without touching business logic.

### 4. Domain Layer (Models & Schemas)
- **Models (`app/Models/`)**: SQLAlchemy ORM classes that map directly to PostgreSQL tables.
- **Schemas (`app/Schemas/`)**: Pydantic models used for data validation, serialization, and type safety across the API boundary.

## 🛠️ Key Technical Components

- **FastAPI**: High-performance async web framework.
- **PostgreSQL**: Primary relational database.
- **SQLAlchemy (Async)**: ORM for database interactions.
- **Celery & RabbitMQ**: Distributed task queue for handling long-running processes like:
    - Large file imports (batch processing).
    - Heavy analytics calculations (SOA).
- **Supabase**:
    - **Auth**: JWT token validation and user management.
    - **Storage**: Object storage for trade screenshots and attachments.
- **Pandas & Scikit-learn**: Used within specific services for data manipulation and clustering algorithms.

## 🚀 Setup & Development

### Prerequisites
- Python 3.11+
- PostgreSQL
- RabbitMQ (for Celery)

### Environment Variables
Create a `.env` file in the `backend/` root.

```env
# Database
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/tradevantage"
DB_USER="user"
DB_PASSWORD="password"
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="tradevantage"

# Environment
ENV="dev" # or 'prod'

# Supabase (Auth & Storage)
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_SERVICE_KEY="your-service-role-key" # For admin tasks
SUPABASE_ANON_KEY="your-anon-key"

# Celery
CELERY_BROKER_URL="amqp://guest:guest@localhost:5672//"
CELERY_RESULT_BACKEND="db+postgresql://user:password@localhost:5432/tradevantage"
```

### Running the Server
```bash
# Ensure you are in the backend/ directory
source venv/bin/activate
uvicorn app.main:app --reload
```

### Running Background Workers
```bash
# In a separate terminal
celery -A app.celery_app worker --loglevel=info -P solo -Q imports,celery
```

### Running Tests
```bash
# Runs all tests with coverage
pytest tests/
```

## 📂 Project Structure (Annotated)

```text
backend/
├── app/
│   ├── Controllers/                    # Request handlers & logic delegation
│   │   ├── analytics_controller.py     # Aggregated stats logic
│   │   ├── import_controller.py        # File upload & task triggering
│   │   ├── soa_controller.py           # Strength & Opportunity Analysis endpoints
│   │   ├── trades_controller.py        # CRUD for trades
│   │   └── ...
│   ├── Infrastructure/                 # External service integrations
│   │   ├── db.py                       # Database connection & session management
│   │   ├── storage.py                  # Supabase Storage client wrapper
│   │   └── supabase_service.py         # Supabase Auth client wrapper
│   ├── Middleware/                     # ASGI Middleware
│   │   └── security_headers.py         # Security headers (CORS, HSTS, etc.)
│   ├── Models/                         # SQLAlchemy ORM Models (Database Schema)
│   │   ├── trade.py                    # Main Trade entity
│   │   ├── playbook.py                 # Playbook & Rules entities
│   │   ├── trading_dna.py              # DNA analysis results
│   │   └── ...
│   ├── Repositories/                   # Database Access Layer (CRUD)
│   │   ├── trade_repository.py         # Complex queries for trades
│   │   ├── soa_repository.py           # Data fetching for analysis
│   │   └── ...
│   ├── Router/                         # API Route Definitions
│   │   ├── routes.py                   # Main router aggregator
│   │   ├── trades_router.py            # Endpoints for /trades
│   │   └── ...
│   ├── Schemas/                        # Pydantic Models (Validation)
│   │   ├── trade.py                    # Input/Output schemas for Trades
│   │   ├── soa.py                      # Schemas for Analysis results
│   │   └── ...
│   ├── Services/                       # Core Business Logic
│   │   ├── metrics/                    # Sub-module for calculation engines
│   │   ├── soa_service.py              # Clustering & Stat Analysis logic (Pandas/Sklearn)
│   │   ├── import_service.py           # Orchestrates file import process
│   │   ├── mt5_parser.py               # Parser for MetaTrader 5 files
│   │   ├── ninjatrader_parser.py       # Parser for NinjaTrader 8 files
│   │   └── ...
│   ├── Utils/                          # Shared utilities
│   │   └── pagination.py               # Pagination helpers
│   ├── celery_app.py                   # Celery application configuration
│   ├── config.py                       # App configuration (Pydantic Settings)
│   ├── main.py                         # FastAPI application entry point
│   └── tasks.py                        # Celery task definitions (Async jobs)
├── tests/                              # Pytest suite
│   ├── controllers/                    # Integration tests for API endpoints
│   ├── services/                       # Unit tests for business logic
│   └── repositories/                   # DB integration tests
├── .env                                # Environment variables (gitignored)
├── conftest.py                         # Pytest fixtures & config
├── requirements.txt                    # Python dependencies
└── README.md                           # This file
```
