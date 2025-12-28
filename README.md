# Trade Vantage

Trade Vantage is a comprehensive trading journal and analytics application designed to help traders track their performance, identify patterns, and improve their strategies. It features a modern Vue.js frontend and a robust FastAPI backend, adhering to clean architecture principles.

For a complete file structure of the project, please refer to [tree.md](tree.md).

## Key Features

- **Trade Journaling**: Log detailed information about each trade, including entry/exit points, fees, commissions, and screenshots.
- **Performance Analytics**: Advanced metrics, equity curve, win/loss ratios, and performance breakdowns by various attributes.
- **Strength & Opportunity Analysis (SOA)**: A sophisticated analytics engine that uses clustering and statistical analysis to provide actionable advice on strategy, risk management, and trading psychology.
- **Discipline Tracking**: Define and track adherence to trading rules and playbooks.
- **Notebook**: A rich-text editor for journaling and note-taking, with the ability to link notes to specific trades.
- **Multi-Platform Import**: Import trades from platforms like NinjaTrader, MT5, and Tradovate.

## Architecture

The project is a monorepo divided into two main applications:

### Backend (`backend/`)
Built with **FastAPI**, the backend follows a strictly layered architecture to separate concerns and ensure maintainability:

1.  **Controllers (`app/Controllers` & `app/Router`)**: Handle HTTP requests, input validation (Pydantic), and response formatting. They delegate business logic to Services.
2.  **Services (`app/Services`)**: Contain the core business logic. They orchestrate operations, handle complex calculations (like SOA), and interact with Repositories for data access.
3.  **Repositories (`app/Repositories`)**: Handle all direct database interactions using **SQLAlchemy**. This layer abstracts the database, making the service layer agnostic of the underlying storage implementation.
4.  **Models (`app/Models`)**: Define the database schema using SQLAlchemy ORM.
5.  **Schemas (`app/Schemas`)**: Pydantic models used for request validation and response serialization.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy (Async), PostgreSQL, Celery (background tasks), Pandas/Scikit-learn (Analytics).

### Frontend (`frontend/`)
A Single Page Application (SPA) built with **Vue.js 3** and **Vite**.

- **State Management**: Uses **Pinia** for centralized state management. Stores are modular and located in `src/stores`.
- **UI Components**: A rich set of reusable UI components (`src/components/ui`) and feature-specific components.
- **Styling**: Uses SCSS with a comprehensive design token system (`tokens/`) for consistent theming (Light/Dark mode).

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL database (or Supabase)

### Backend Setup

1.  **Navigate to the backend directory:**
    ```sh
    cd backend
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    Create a `.env` file in the `backend/` directory and populate it with your database URL and Supabase keys:
    ```env
    DATABASE_URL="postgresql+asyncpg://user:password@host:port/dbname"
    SUPABASE_URL="https://your-supabase-url.supabase.co"
    SUPABASE_SERVICE_KEY="your-supabase-service-key"
    SUPABASE_ANON_KEY="your-supabase-anon-key"
    ```

5.  **Run the development server:**
    ```sh
    uvicorn app.main:app --reload
    ```
    The backend API will be available at `http://127.0.0.1:8000`.

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```sh
    cd frontend
    ```

2.  **Install dependencies:**
    ```sh
    npm install
    ```

3.  **Configure environment variables:**
    Create a `.env.local` file in the `frontend/` directory and add the backend API URL and Supabase public key:
    ```env
    VITE_API_BASE_URL="http://127.0.0.1:8000/api/v1"
    VITE_SUPABASE_URL="https://your-supabase-url.supabase.co"
    VITE_SUPABASE_ANON_KEY="your-supabase-anon-key"
    ```

4.  **Run the development server:**
    ```sh
    npm run dev
    ```
    The frontend application will be available at `http://127.0.0.1:5173`.

## Strength & Opportunity Analysis (SOA) Feature

The SOA feature provides deep insights by analyzing trade data through a multi-level process.

- **Level 1 (Clustering)**: Trades are grouped into clusters based on 7 key performance vectors (e.g., Profit Efficiency, Stress Ratio). This helps identify distinct types of trading outcomes.
- **Level 2 (Causal Analysis)**: The system analyzes the correlation between trade attributes (like playbooks, tags, mistakes) and the performance clusters, revealing what factors contribute to specific outcomes.
- **Level 3 (Parametric Optimization)**: The engine calculates optimal Stop Loss and Take Profit levels by analyzing the historical performance of winning trades.
- **Level 4 (Predictive Metrics)**: Psychological patterns are identified by analyzing R-multiple autocorrelation and drawdown Z-scores.

This numerical analysis is then translated into human-readable, actionable advice by the **SOA Advisor** service in the backend, which is displayed directly in the SOA Dashboard Widget on the frontend.
