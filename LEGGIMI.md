# Trade Vantage

Trade Vantage è un'applicazione completa per il trading journal e l'analisi, progettata per aiutare i trader a monitorare le loro prestazioni, identificare pattern e migliorare le loro strategie. Presenta un frontend moderno in Vue.js e un robusto backend in FastAPI, aderendo ai principi dell'architettura pulita.

Per una struttura completa dei file del progetto, consultare [tree.md](tree.md).

## Caratteristiche Principali

- **Diario di Trading**: Registra informazioni dettagliate su ogni operazione, inclusi punti di ingresso/uscita, commissioni e screenshot.
- **Analisi delle Prestazioni**: Metriche avanzate, curva dell'equity, rapporti vincita/perdita e ripartizioni delle prestazioni per vari attributi.
- **Strength & Opportunity Analysis (SOA)**: Un sofisticato motore di analisi che utilizza il clustering e l'analisi statistica per fornire consigli pratici su strategia, gestione del rischio e psicologia del trading.
- **Tracciamento della Disciplina**: Definisci e traccia l'aderenza alle regole di trading e ai playbook.
- **Notebook**: Un editor rich-text per diario e appunti, con la possibilità di collegare le note a operazioni specifiche.
- **Importazione Multi-Piattaforma**: Importa operazioni da piattaforme come NinjaTrader, MT5 e Tradovate.

## Architettura

Il progetto è un monorepo diviso in due applicazioni principali:

### Backend (`backend/`)
Costruito con **FastAPI**, il backend segue un'architettura rigorosamente a livelli per separare le responsabilità e garantire la manutenibilità:

1.  **Controllers (`app/Controllers` & `app/Router`)**: Gestiscono le richieste HTTP, la validazione dell'input (Pydantic) e la formattazione della risposta. Delegano la logica di business ai Service.
2.  **Services (`app/Services`)**: Contengono la logica di business principale. Orchestrano le operazioni, gestiscono calcoli complessi (come SOA) e interagiscono con i Repository per l'accesso ai dati.
3.  **Repositories (`app/Repositories`)**: Gestiscono tutte le interazioni dirette con il database utilizzando **SQLAlchemy**. Questo livello astrae il database, rendendo il livello di servizio agnostico rispetto all'implementazione sottostante dello storage.
4.  **Models (`app/Models`)**: Definiscono lo schema del database utilizzando l'ORM SQLAlchemy.
5.  **Schemas (`app/Schemas`)**: Modelli Pydantic utilizzati per la validazione delle richieste e la serializzazione delle risposte.

**Stack Tecnologico:** Python 3.11+, FastAPI, SQLAlchemy (Async), PostgreSQL, Celery (task in background), Pandas/Scikit-learn (Analisi).

### Frontend (`frontend/`)
Una Single Page Application (SPA) costruita con **Vue.js 3** e **Vite**.

- **Gestione dello Stato**: Utilizza **Pinia** per la gestione centralizzata dello stato. Gli store sono modulari e situati in `src/stores`.
- **Componenti UI**: Un ricco set di componenti UI riutilizzabili (`src/components/ui`) e componenti specifici per le funzionalità.
- **Stile**: Utilizza SCSS con un sistema completo di token di design (`tokens/`) per temi coerenti (Modalità Chiara/Scura).

## Per Iniziare

### Prerequisiti

- Python 3.11+
- Node.js 20+
- Database PostgreSQL (o Supabase)

### Configurazione Backend

1.  **Naviga nella directory del backend:**
    ```sh
    cd backend
    ```

2.  **Crea e attiva un ambiente virtuale:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # Su Windows usa `venv\Scripts\activate`
    ```

3.  **Installa le dipendenze:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Configura le variabili d'ambiente:**
    Crea un file `.env` nella directory `backend/` e popolalo con l'URL del tuo database e le chiavi Supabase:
    ```env
    DATABASE_URL="postgresql+asyncpg://user:password@host:port/dbname"
    SUPABASE_URL="https://your-supabase-url.supabase.co"
    SUPABASE_SERVICE_KEY="your-supabase-service-key"
    SUPABASE_ANON_KEY="your-supabase-anon-key"
    ```

5.  **Avvia il server di sviluppo:**
    ```sh
    uvicorn app.main:app --reload
    ```
    L'API backend sarà disponibile su `http://127.0.0.1:8000`.

### Configurazione Frontend

1.  **Naviga nella directory del frontend:**
    ```sh
    cd frontend
    ```

2.  **Installa le dipendenze:**
    ```sh
    npm install
    ```

3.  **Configura le variabili d'ambiente:**
    Crea un file `.env.local` nella directory `frontend/` e aggiungi l'URL base dell'API backend e la chiave pubblica Supabase:
    ```env
    VITE_API_BASE_URL="http://127.0.0.1:8000/api/v1"
    VITE_SUPABASE_URL="https://your-supabase-url.supabase.co"
    VITE_SUPABASE_ANON_KEY="your-supabase-anon-key"
    ```

4.  **Avvia il server di sviluppo:**
    ```sh
    npm run dev
    ```
    L'applicazione frontend sarà disponibile su `http://127.0.0.1:5173`.

## Funzionalità Strength & Opportunity Analysis (SOA)

La funzionalità SOA fornisce approfondimenti dettagliati analizzando i dati di trading attraverso un processo a più livelli.

- **Livello 1 (Clustering)**: Le operazioni vengono raggruppate in cluster basati su 7 vettori chiave di prestazione (es. Efficienza del Profitto, Rapporto di Stress). Questo aiuta a identificare tipi distinti di risultati di trading.
- **Livello 2 (Analisi Causale)**: Il sistema analizza la correlazione tra gli attributi dell'operazione (come playbook, tag, errori) e i cluster di prestazioni, rivelando quali fattori contribuiscono a risultati specifici.
- **Livello 3 (Ottimizzazione Parametrica)**: Il motore calcola i livelli ottimali di Stop Loss e Take Profit analizzando le prestazioni storiche delle operazioni vincenti.
- **Livello 4 (Metriche Predittive)**: I pattern psicologici vengono identificati analizzando l'autocorrelazione multipla R e gli Z-score del drawdown.

Questa analisi numerica viene poi tradotta in consigli pratici e leggibili dal servizio **SOA Advisor** nel backend, che viene visualizzato direttamente nel Widget Dashboard SOA sul frontend.
