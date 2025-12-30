# Trade Vantage

Trade Vantage è una piattaforma di trading journal e analisi di livello enterprise, progettata per aiutare i trader a monitorare le performance, identificare pattern comportamentali e migliorare sistematicamente le proprie strategie. Combina un frontend moderno e reattivo in Vue.js con un backend robusto e scalabile in FastAPI, seguendo i principi della Clean Architecture.

Per una struttura completa dei file del progetto, consultare [tree.md](tree.md).

## Caratteristiche Principali

### 📊 Journaling & Analisi Avanzata
- **Diario di Trading**: Registra dati dettagliati su ogni operazione, inclusi punti di ingresso/uscita, commissioni e screenshot multipli. Supporta note rich-text collegate a trade specifici.
- **Analisi delle Prestazioni**: Calcolo in tempo reale di metriche avanzate (Win Rate, Profit Factor, Expectancy, Sharpe Ratio, Sortino Ratio), curve dell'equity interattive e distribuzioni P&L.
- **Importazione Multi-Piattaforma**: Importa senza problemi lo storico delle operazioni da **NinjaTrader 8**, **MetaTrader 5 (MT5)** e **Tradovate** tramite drag-and-drop. Il sistema gestisce automaticamente la deduplicazione e la mappatura dei conti.

### 🧬 Trading DNA
- **Analisi Comportamentale**: Un motore unico che analizza la tua storia di trading per identificare le "Golden Combos" (condizioni in cui performi meglio) e le "Toxic Combos" (condizioni che portano a perdite).
- **Analisi dei Cluster**: Raggruppa le operazioni in base a stati psicologici, tag ed errori per rivelare pattern nascosti nel tuo processo decisionale.

### 🧠 Strength & Opportunity Analysis (SOA)
- **Intelligence Multi-Livello**:
    - **Livello 1 (Clustering)**: Raggruppa le operazioni utilizzando il clustering K-Means su 7 vettori di performance (es. Efficienza, Rapporto di Stress).
    - **Livello 2 (Analisi Causale)**: Correlazione dei risultati con Playbook, Tag ed Errori.
    - **Livello 3 (Ottimizzazione)**: Calcola i livelli ottimali di Stop Loss e Take Profit basandosi sui dati storici "MFE/MAE".
    - **Livello 4 (Predittivo)**: Rileva il "tilt" psicologico utilizzando l'autocorrelazione del multiplo R.
- **Advisor**: Fornisce consigli pratici e leggibili generati dalle evidenze statistiche.

### 🛡️ Disciplina & Psicologia
- **Checklist Giornaliera**: Checklist interattive pre-market e post-market per garantire l'aderenza al processo.
- **Heatmap Calendario**: Visualizza l'attività di trading e il rispetto delle regole nel tempo.
- **Impatto delle Notizie**: Traccia come gli eventi di notizie ad alto impatto influenzano le tue performance di trading.
- **Tracciamento Errori**: Tagga le operazioni con errori specifici (es. "FOMO", "Revenge Trading") per quantificarne il costo.

### 📒 Notebook & Knowledge Base
- **Editor Rich Text**: Un editor in stile Notion per il diario giornaliero, note strategiche e ricerca.
- **Organizzazione a Cartelle**: Struttura gerarchica per organizzare le note per strategia, sessione o argomento.
- **Playbook**: Definisci strategie di trading dettagliate (Playbook) con regole specifiche e traccia la tua aderenza ad esse su ogni operazione.

### 🎨 Dashboard Personalizzabile
- **Sistema a Widget**: Una dashboard modulare dove gli utenti possono aggiungere, rimuovere e riorganizzare widget (es. Operazioni Recenti, Grafico Win/Loss, Curva Equity, Calendario) per adattarli al proprio flusso di lavoro.
- **Modalità Chiara/Scura**: Temi completamente supportati tramite un sistema completo di token di design.

## Architettura

Il progetto è un monorepo che implementa un pattern di **Clean Architecture** per garantire scalabilità, testabilità e separazione delle responsabilità.

### Backend (`backend/`)
Costruito con **FastAPI** (Python 3.11+), il backend è strutturato in livelli distinti:

1.  **Controllers (`app/Controllers`)**: Gestiscono le richieste HTTP, la validazione Pydantic e la dependency injection.
2.  **Services (`app/Services`)**: Incapsulano la logica di business. Questo livello orchestra operazioni complesse come i calcoli SOA, il parsing dei file e l'arricchimento dei dati.
3.  **Repositories (`app/Repositories`)**: Gestiscono l'accesso ai dati utilizzando **SQLAlchemy (Async)**. Questo astrae il database, permettendo test facili e potenziali cambi di storage.
4.  **Models (`app/Models`)**: Definiscono lo schema del database.
5.  **Infrastruttura**:
    - **Celery & RabbitMQ**: Gestisce task asincroni come importazioni di file di grandi dimensioni e calcoli analitici pesanti per mantenere l'API reattiva.
    - **Integrazione Supabase**: Utilizza Supabase per l'Autenticazione sicura (JWT) e l'Object Storage (screenshot/immagini).

**Stack Tecnologico:** Python 3.11, FastAPI, PostgreSQL, SQLAlchemy (Async), Celery, RabbitMQ, Pandas/Scikit-learn (Analytics), Supabase (Auth/Storage).

### Frontend (`frontend/`)
Una Single Page Application (SPA) costruita con **Vue.js 3** e **Vite**.

- **Gestione dello Stato**: **Pinia** gestisce lo stato dell'applicazione, con store modulari per Operazioni, Auth, UI, ecc.
- **Design dei Componenti**: Utilizza un pattern a componenti compositi con una ricca libreria di elementi UI atomici (`src/components/ui`) stilizzati tramite variabili SCSS/token.
- **Visualizzazione**: Integra **Chart.js** e componenti SVG personalizzati per la visualizzazione dati ad alte prestazioni.

## Per Iniziare

### Prerequisiti

- Python 3.11+
- Node.js 20+
- Database PostgreSQL
- RabbitMQ (per i task in background)
- Account Supabase (per Auth & Storage)

### Configurazione Backend

1.  **Naviga nella directory backend:**
    ```sh
    cd backend
    ```

2.  **Ambiente Virtuale:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

3.  **Installa Dipendenze:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Variabili d'Ambiente:**
    Crea un file `.env` in `backend/` con:
    ```env
    DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/tradevantage"
    SUPABASE_URL="https://your-project.supabase.co"
    SUPABASE_SERVICE_KEY="your-service-role-key"
    CELERY_BROKER_URL="amqp://guest:guest@localhost:5672//"
    ```

5.  **Avvia Server:**
    ```sh
    uvicorn app.main:app --reload
    ```
    Documentazione API disponibile su: `http://127.0.0.1:8000/docs`

6.  **Avvia Worker Celery:**
    ```sh
    celery -A app.celery_app worker --loglevel=info -P solo
    ```

### Configurazione Frontend

1.  **Naviga nella directory frontend:**
    ```sh
    cd frontend
    ```

2.  **Installa Dipendenze:**
    ```sh
    npm install
    ```

3.  **Variabili d'Ambiente:**
    Crea un file `.env.local` in `frontend/` con:
    ```env
    VITE_API_BASE_URL="http://127.0.0.1:8000/api/v1"
    VITE_SUPABASE_URL="https://your-project.supabase.co"
    VITE_SUPABASE_ANON_KEY="your-anon-key"
    ```

4.  **Avvia Server di Sviluppo:**
    ```sh
    npm run dev
    ```
    App disponibile su: `http://127.0.0.1:5173`
