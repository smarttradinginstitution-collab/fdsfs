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
│   │   ├── __init__.py                 # Controller package init
│   │   ├── analytics_controller.py     # Aggregated stats logic
│   │   ├── asset_alias_controller.py   # Asset mapping logic
│   │   ├── asset_class_controller.py   # Asset class management
│   │   ├── asset_controller.py         # Asset management
│   │   ├── asset_market_controller.py  # Market session management
│   │   ├── auth_controller.py          # Authentication handlers
│   │   ├── broker_controller.py        # Broker management
│   │   ├── general_account_controller.py # User account management
│   │   ├── import_controller.py        # File upload & task triggering
│   │   ├── mistake_controller.py       # Mistake tracking logic
│   │   ├── news_impact_controller.py   # News impact event logic
│   │   ├── news_impacts_group_controller.py # News impact grouping
│   │   ├── note_template_controller.py # Notebook templates
│   │   ├── notebook_controller.py      # Notebook & notes logic
│   │   ├── platform_controller.py      # Trading platform management
│   │   ├── playbook_controller.py      # Playbook strategy logic
│   │   ├── psychology_state_controller.py # Psychology state tracking
│   │   ├── roles_controller.py         # RBAC role management
│   │   ├── rule_playbook_controller.py # Playbook rules logic
│   │   ├── rules_group_playbook_controller.py # Rule grouping
│   │   ├── soa_controller.py           # Strength & Opportunity Analysis endpoints
│   │   ├── tag_controller.py           # Tag management
│   │   ├── tags_group_controller.py    # Tag grouping
│   │   ├── trades_controller.py        # CRUD for trades
│   │   ├── trading_account_controller.py # Trading account management
│   │   ├── trading_dna_controller.py   # Trading DNA analysis
│   │   ├── user_dashboard_layout_controller.py # Dashboard layout persistence
│   │   ├── user_roles_controller.py    # User-Role association
│   │   └── users_controller.py         # User profile management
│   ├── Infrastructure/                 # External service integrations
│   │   ├── __init__.py                 # Infrastructure package init
│   │   ├── db.py                       # Database connection & session management
│   │   ├── storage.py                  # Supabase Storage client wrapper
│   │   └── supabase_service.py         # Supabase Auth client wrapper
│   ├── Middleware/                     # ASGI Middleware
│   │   └── security_headers.py         # Security headers (CORS, HSTS, etc.)
│   ├── Models/                         # SQLAlchemy ORM Models (Database Schema)
│   │   ├── __init__.py                 # Models package init
│   │   ├── asset.py                    # Asset entity
│   │   ├── asset_alias.py              # Asset alias entity
│   │   ├── asset_class.py              # Asset class entity
│   │   ├── asset_market.py             # Market session entity
│   │   ├── auth_user.py                # User entity
│   │   ├── broker.py                   # Broker entity
│   │   ├── broker_asset_class.py       # Broker-Asset relation
│   │   ├── broker_platform.py          # Broker-Platform relation
│   │   ├── daily_rule_instance.py      # Daily rule tracking
│   │   ├── discipline_rule.py          # Discipline rule entity
│   │   ├── discipline_settings.py      # Discipline configuration
│   │   ├── enums.py                    # Global enumerations
│   │   ├── general_account.py          # General account entity
│   │   ├── image.py                    # Image/Screenshot entity
│   │   ├── import_run.py               # Import job tracking
│   │   ├── manual_rule.py              # Manual rule entity
│   │   ├── mistake.py                  # Mistake entity
│   │   ├── news_impact.py              # News impact entity
│   │   ├── news_impacts_group.py       # News impact group entity
│   │   ├── note.py                     # Note entity
│   │   ├── note_template.py            # Note template entity
│   │   ├── notebook_folder.py          # Notebook folder entity
│   │   ├── notes_note_templates.py     # Note-Template relation
│   │   ├── platform.py                 # Trading platform entity
│   │   ├── playbook.py                 # Playbook entity
│   │   ├── psychology_state.py         # Psychology state entity
│   │   ├── role.py                     # Role entity
│   │   ├── rule_playbook.py            # Playbook rule entity
│   │   ├── rules_group_playbook.py     # Rule group entity
│   │   ├── tag.py                      # Tag entity
│   │   ├── tags_group.py               # Tag group entity
│   │   ├── trade.py                    # Main Trade entity
│   │   ├── trades_mistakes.py          # Trade-Mistake relation
│   │   ├── trades_news_impacts.py      # Trade-News relation
│   │   ├── trades_psychology.py        # Trade-Psychology relation
│   │   ├── trades_tags.py              # Trade-Tag relation
│   │   ├── trading_account.py          # Trading account entity
│   │   ├── user_dashboard_layout.py    # Dashboard layout entity
│   │   └── user_role.py                # User-Role relation
│   ├── Repositories/                   # Database Access Layer (CRUD)
│   │   ├── __init__.py                 # Repositories package init
│   │   ├── asset_alias_repository.py   # Asset alias access
│   │   ├── asset_class_repository.py   # Asset class access
│   │   ├── asset_market_repository.py  # Asset market access
│   │   ├── asset_repository.py         # Asset access
│   │   ├── auth_user_repository.py     # User access
│   │   ├── base_repository.py          # Generic repository base class
│   │   ├── broker_asset_class_repository.py # Broker-Asset access
│   │   ├── broker_repository.py        # Broker access
│   │   ├── daily_rule_instance_repository.py # Daily rule access
│   │   ├── discipline_settings_repository.py # Discipline settings access
│   │   ├── general_account_repository.py # General account access
│   │   ├── image_repository.py         # Image access
│   │   ├── manual_rule_repository.py   # Manual rule access
│   │   ├── mistake_repository.py       # Mistake access
│   │   ├── news_impact_repository.py   # News impact access
│   │   ├── news_impacts_group_repository.py # News impact group access
│   │   ├── note_repository.py          # Note access
│   │   ├── note_template_repository.py # Note template access
│   │   ├── notebook_folder_repository.py # Notebook folder access
│   │   ├── platform_repository.py      # Platform access
│   │   ├── playbook_repository.py      # Playbook access
│   │   ├── psychology_state_repository.py # Psychology state access
│   │   ├── role_repository.py          # Role access
│   │   ├── rule_playbook_repository.py # Playbook rule access
│   │   ├── rules_group_playbook_repository.py # Rule group access
│   │   ├── tag_repository.py           # Tag access
│   │   ├── tags_group_repository.py    # Tag group access
│   │   ├── trade_repository.py         # Complex queries for trades
│   │   ├── trading_account_repository.py # Trading account access
│   │   ├── user_dashboard_layout_repository.py # Dashboard layout access
│   │   └── user_role_repository.py     # User-Role access
│   ├── Router/                         # API Route Definitions
│   │   ├── __init__.py                 # Router package init
│   │   ├── analytics_router.py         # Analytics routes
│   │   ├── asset_alias_router.py       # Asset alias routes
│   │   ├── asset_class_router.py       # Asset class routes
│   │   ├── asset_market_router.py      # Asset market routes
│   │   ├── asset_router.py             # Asset routes
│   │   ├── auth.py                     # Authentication routes
│   │   ├── broker_router.py            # Broker routes
│   │   ├── daily_checklist_router.py   # Daily checklist routes
│   │   ├── dependencies.py             # API dependencies (Auth, etc.)
│   │   ├── discipline_settings_router.py # Discipline settings routes
│   │   ├── general_account_router.py   # General account routes
│   │   ├── image_router.py             # Image routes
│   │   ├── import_router.py            # Import routes
│   │   ├── manual_rule_router.py       # Manual rule routes
│   │   ├── mistake_router.py           # Mistake routes
│   │   ├── news_impact_router.py       # News impact routes
│   │   ├── news_impacts_group_router.py # News impact group routes
│   │   ├── notebook_router.py          # Notebook routes
│   │   ├── platform_router.py          # Platform routes
│   │   ├── playbook_router.py          # Playbook routes
│   │   ├── psychology_state_router.py  # Psychology state routes
│   │   ├── routes.py                   # Main router aggregator
│   │   ├── rule_playbook_router.py     # Playbook rule routes
│   │   ├── rule_statistics_router.py   # Rule stats routes
│   │   ├── rules_group_playbook_router.py # Rule group routes
│   │   ├── soa_router.py               # SOA routes
│   │   ├── tag_router.py               # Tag routes
│   │   ├── tags_group_router.py        # Tag group routes
│   │   ├── trades_router.py            # Trades routes
│   │   ├── trading_account_router.py   # Trading account routes
│   │   └── trading_dna_router.py       # Trading DNA routes
│   ├── Schemas/                        # Pydantic Models (Validation)
│   │   ├── discipline/                 # Nested schemas for discipline
│   │   ├── __init__.py                 # Schemas package init
│   │   ├── analytics.py                # Analytics schemas
│   │   ├── asset.py                    # Asset schemas
│   │   ├── asset_alias.py              # Asset alias schemas
│   │   ├── asset_class.py              # Asset class schemas
│   │   ├── asset_market.py             # Asset market schemas
│   │   ├── auth_session.py             # Auth session schemas
│   │   ├── auth_user.py                # User schemas
│   │   ├── broker.py                   # Broker schemas
│   │   ├── broker_asset_class.py       # Broker-Asset schemas
│   │   ├── daily_rule_instance_schema.py # Daily rule schemas
│   │   ├── discipline_settings_schema.py # Discipline settings schemas
│   │   ├── general_account.py          # General account schemas
│   │   ├── image.py                    # Image schemas
│   │   ├── import_run.py               # Import run schemas
│   │   ├── manual_rule_schema.py       # Manual rule schemas
│   │   ├── mistake.py                  # Mistake schemas
│   │   ├── news_impact.py              # News impact schemas
│   │   ├── news_impacts_group.py       # News impact group schemas
│   │   ├── note_template.py            # Note template schemas
│   │   ├── notebook.py                 # Notebook schemas
│   │   ├── platform.py                 # Platform schemas
│   │   ├── playbook.py                 # Playbook schemas
│   │   ├── psychology_state.py         # Psychology state schemas
│   │   ├── role.py                     # Role schemas
│   │   ├── rule_playbook.py            # Playbook rule schemas
│   │   ├── rules_group_playbook.py     # Rule group schemas
│   │   ├── soa.py                      # SOA schemas
│   │   ├── stats.py                    # Statistics schemas
│   │   ├── tag.py                      # Tag schemas
│   │   ├── tags_group.py               # Tag group schemas
│   │   ├── trade.py                    # Trade schemas
│   │   ├── trades_tags.py              # Trade-Tag schemas
│   │   ├── trading_account.py          # Trading account schemas
│   │   ├── trading_dna.py              # Trading DNA schemas
│   │   ├── user_dashboard_layout.py    # Dashboard layout schemas
│   │   ├── user_role.py                # User-Role schemas
│   │   └── vantage_score.py            # Vantage score schemas
│   ├── Services/                       # Core Business Logic
│   │   ├── metrics/                    # Metric calculation engines
│   │   ├── __init__.py                 # Services package init
│   │   ├── analytics_service.py        # Analytics business logic
│   │   ├── broker_service.py           # Broker logic
│   │   ├── discipline_settings_service.py # Discipline logic
│   │   ├── general_account_service.py  # General account logic
│   │   ├── image_service.py            # Image handling logic
│   │   ├── import_service.py           # Import orchestration
│   │   ├── jwt_service.py              # JWT handling
│   │   ├── mt5_parser.py               # MT5 file parsing
│   │   ├── ninjatrader_parser.py       # NinjaTrader file parsing
│   │   ├── note_template_service.py    # Note template logic
│   │   ├── notebook_service.py         # Notebook logic
│   │   ├── playbook_analytics_service.py # Playbook analytics
│   │   ├── playbook_service.py         # Playbook logic
│   │   ├── role_service.py             # Role logic
│   │   ├── rule_statistics_service.py  # Rule stats logic
│   │   ├── soa_advisor.py              # SOA advice generation
│   │   ├── soa_service.py              # SOA calculation engine
│   │   ├── supabase_client.py          # Supabase client factory
│   │   ├── trade_service.py            # Trade logic
│   │   ├── trading_account_service.py  # Trading account logic
│   │   ├── trading_dna_service.py      # Trading DNA logic
│   │   ├── tradovate_parser.py         # Tradovate file parsing
│   │   ├── user_dashboard_layout_service.py # Dashboard logic
│   │   └── user_service.py             # User logic
│   ├── Utils/                          # Shared utilities
│   │   ├── __init__.py                 # Utils package init
│   │   └── pagination.py               # Pagination helpers
│   ├── celery_app.py                   # Celery application configuration
│   ├── config.py                       # App configuration (Pydantic Settings)
│   ├── main.py                         # FastAPI application entry point
│   └── tasks.py                        # Celery task definitions (Async jobs)
├── tests/                              # Pytest suite
│   ├── controllers/                    # Integration tests for API endpoints
│   ├── repositories/                   # Integration tests for Repositories
│   ├── services/                       # Unit tests for Services
│   └── utils/                          # Unit tests for Utilities
├── .env                                # Environment variables (gitignored)
├── conftest.py                         # Pytest fixtures & config
├── requirements.txt                    # Python dependencies
└── README.md                           # This file
```
