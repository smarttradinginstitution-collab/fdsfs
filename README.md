# Trade Vantage

Trade Vantage is a comprehensive, enterprise-grade trading journal and analytics platform designed to help traders track performance, identify behavioral patterns, and systematically improve their strategies. It combines a modern, responsive Vue.js frontend with a robust, scalable FastAPI backend, adhering to clean architecture principles.

For a complete file structure of the project, please refer to [tree.md](tree.md).

## Key Features

### 📊 Advanced Journaling & Analytics
- **Trade Journaling**: Log detailed trade data including entry/exit points, commissions, fees, and multiple screenshots. Supports rich-text notes linked to specific trades.
- **Performance Analytics**: Real-time calculation of advanced metrics (Win Rate, Profit Factor, Expectancy, Sharpe Ratio, Sortino Ratio), interactive equity curves, and P&L distributions.
- **Multi-Platform Import**: Seamlessly import trade history from **NinjaTrader 8**, **MetaTrader 5 (MT5)**, and **Tradovate** via drag-and-drop. The system handles deduplication and account mapping automatically.

### 🧬 Trading DNA
- **Behavioral Analysis**: A unique engine that analyzes your trading history to identify "Golden Combos" (conditions where you perform best) and "Toxic Combos" (conditions leading to losses).
- **Cluster Analysis**: Groups trades based on psychological states, tags, and mistakes to reveal hidden patterns in your decision-making process.

### 🧠 Strength & Opportunity Analysis (SOA)
- **Multi-Level Intelligence**:
    - **Level 1 (Clustering)**: Groups trades using K-Means clustering on 7 performance vectors (e.g., Efficiency, Stress Ratio).
    - **Level 2 (Causal Analysis)**: Correlates outcomes with Playbooks, Tags, and Mistakes.
    - **Level 3 (Optimization)**: Calculates optimal Stop Loss and Take Profit levels based on historical "MFE/MAE" data.
    - **Level 4 (Predictive)**: Detects psychological tilt using R-multiple autocorrelation.
- **Advisor**: Provides human-readable, actionable advice generated from statistical findings.

### 🛡️ Discipline & Psychology
- **Daily Checklist**: Interactive pre-market and post-market checklists to ensure process adherence.
- **Calendar Heatmap**: Visualizes trading activity and rule compliance over time.
- **News Impact**: Tracks how high-impact news events affect your trading performance.
- **Mistake Tracking**: Tag trades with specific mistakes (e.g., "FOMO", "Revenge Trading") to quantify their cost.

### 📒 Notebook & Knowledge Base
- **Rich Text Editor**: A Notion-style editor for daily journaling, strategy notes, and research.
- **Folder Organization**: Hierarchical structure to organize notes by strategy, session, or topic.
- **Playbooks**: Define detailed trading strategies (Playbooks) with specific rules and track your adherence to them on every trade.

### 🎨 Customizable Dashboard
- **Widget System**: A modular dashboard where users can add, remove, and rearrange widgets (e.g., Recent Trades, Win/Loss Gauge, Equity Curve, Calendar) to suit their workflow.
- **Dark/Light Mode**: Fully supported theming via a comprehensive design token system.

## Architecture

The project is a monorepo implementing a **Clean Architecture** pattern to ensure scalability, testability, and separation of concerns.

### Backend (`backend/`)
Built with **FastAPI** (Python 3.11+), the backend is structured into distinct layers:

1.  **Controllers (`app/Controllers`)**: Handle HTTP requests, Pydantic validation, and dependency injection.
2.  **Services (`app/Services`)**: Encapsulate business logic. This layer orchestrates complex operations like SOA calculations, file parsing, and data enrichment.
3.  **Repositories (`app/Repositories`)**: Manage data access using **SQLAlchemy (Async)**. This abstracts the database, allowing for easy testing and potential storage swaps.
4.  **Models (`app/Models`)**: Define the database schema.
5.  **Infrastructure**:
    - **Celery & RabbitMQ**: Handles asynchronous tasks like large file imports and heavy analytics computations to keep the API responsive.
    - **Supabase Integration**: Uses Supabase for secure Authentication (JWT) and Object Storage (screenshots/images).

**Tech Stack:** Python 3.11, FastAPI, PostgreSQL, SQLAlchemy (Async), Celery, RabbitMQ, Pandas/Scikit-learn (Analytics), Supabase (Auth/Storage).

### Frontend (`frontend/`)
A Single Page Application (SPA) built with **Vue.js 3** and **Vite**.

- **State Management**: **Pinia** stores manage application state, with modular stores for Trades, Auth, UI, etc.
- **Component Design**: Uses a composite component pattern with a rich library of atomic UI elements (`src/components/ui`) styled via SCSS variables/tokens.
- **Visualization**: Integrates **Chart.js** and custom SVG components for high-performance data visualization.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL database
- RabbitMQ (for background tasks)
- Supabase Account (for Auth & Storage)

### Backend Setup

1.  **Navigate to backend:**
    ```sh
    cd backend
    ```

2.  **Virtual Environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Environment Variables:**
    Create a `.env` file in `backend/` with:
    ```env
    DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/tradevantage"
    SUPABASE_URL="https://your-project.supabase.co"
    SUPABASE_SERVICE_KEY="your-service-role-key"
    CELERY_BROKER_URL="amqp://guest:guest@localhost:5672//"
    ```

5.  **Run Server:**
    ```sh
    uvicorn app.main:app --reload
    ```
    API docs available at: `http://127.0.0.1:8000/docs`

6.  **Run Celery Worker:**
    ```sh
    celery -A app.celery_app worker --loglevel=info -P solo
    ```

### Frontend Setup

1.  **Navigate to frontend:**
    ```sh
    cd frontend
    ```

2.  **Install Dependencies:**
    ```sh
    npm install
    ```

3.  **Environment Variables:**
    Create a `.env.local` file in `frontend/` with:
    ```env
    VITE_API_BASE_URL="http://127.0.0.1:8000/api/v1"
    VITE_SUPABASE_URL="https://your-project.supabase.co"
    VITE_SUPABASE_ANON_KEY="your-anon-key"
    ```

4.  **Run Dev Server:**
    ```sh
    npm run dev
    ```
    App available at: `http://127.0.0.1:5173`
