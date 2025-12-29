# Trade Vantage - Backend API

Questa è l'API backend principale per la piattaforma Trade Vantage. Costruita con **FastAPI**, funge da sistema nervoso centrale per l'elaborazione dei dati, l'analisi e la persistenza. Aderisce a un rigoroso pattern di **Clean Architecture** per garantire scalabilità, manutenibilità e testabilità.

## 🏗️ Architettura & Design Patterns

Il backend è strutturato in livelli distinti, ognuno con una responsabilità specifica. I dati fluiscono dai livelli esterni (API) verso l'interno, dove risiedono la logica di business e l'accesso ai dati.

### 1. Livello di Presentazione (Routers & Controllers)
- **Routers (`app/Router/`)**: Definiscono gli endpoint HTTP, gestiscono la dependency injection (FastAPI `Depends`) e instradano le richieste ai controller appropriati. Applicano anche gli ambiti di autenticazione e autorizzazione.
- **Controllers (`app/Controllers/`)**: Il punto di ingresso per la logica dell'applicazione. Ricevono schemi Pydantic, eseguono la validazione iniziale e chiamano i metodi dei Service appropriati. Sono responsabili della formattazione della risposta HTTP.

### 2. Livello di Logica di Business (Services)
- **Services (`app/Services/`)**: Contengono le regole di business principali e i casi d'uso. È qui che avviene la "magia".
    - **SOA Service**: Gestisce analisi statistiche complesse utilizzando Pandas e Scikit-learn.
    - **Parsers**: Servizi dedicati per il parsing dei file di trade da NinjaTrader, MT5, ecc.
    - **Orchestrators**: Servizi che coordinano più repository (es. `ImportService` che gestisce caricamenti file, parsing e inserimento nel database).

### 3. Livello di Accesso ai Dati (Repositories)
- **Repositories (`app/Repositories/`)**: Astraggono le interazioni con il database. Utilizzano **SQLAlchemy (Async)** per eseguire operazioni CRUD. Questo isolamento ci permette di cambiare il database sottostante o ottimizzare le query senza toccare la logica di business.

### 4. Livello di Dominio (Models & Schemas)
- **Models (`app/Models/`)**: Classi ORM SQLAlchemy che mappano direttamente le tabelle PostgreSQL.
- **Schemas (`app/Schemas/`)**: Modelli Pydantic utilizzati per la validazione dei dati, la serializzazione e la sicurezza dei tipi attraverso il confine dell'API.

## 🛠️ Componenti Tecnici Chiave

- **FastAPI**: Framework web asincrono ad alte prestazioni.
- **PostgreSQL**: Database relazionale primario.
- **SQLAlchemy (Async)**: ORM per le interazioni con il database.
- **Celery & RabbitMQ**: Coda di task distribuiti per gestire processi a lunga esecuzione come:
    - Importazioni di file di grandi dimensioni (elaborazione batch).
    - Calcoli analitici pesanti (SOA).
- **Supabase**:
    - **Auth**: Validazione token JWT e gestione utenti.
    - **Storage**: Object storage per screenshot e allegati dei trade.
- **Pandas & Scikit-learn**: Utilizzati all'interno di servizi specifici per la manipolazione dei dati e algoritmi di clustering.

## 🚀 Setup & Sviluppo

### Prerequisiti
- Python 3.11+
- PostgreSQL
- RabbitMQ (per Celery)

### Variabili d'Ambiente
Crea un file `.env` nella root di `backend/`.

```env
# Database
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/tradevantage"
DB_USER="user"
DB_PASSWORD="password"
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="tradevantage"

# Environment
ENV="dev" # o 'prod'

# Supabase (Auth & Storage)
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_SERVICE_KEY="your-service-role-key" # Per task admin
SUPABASE_ANON_KEY="your-anon-key"

# Celery
CELERY_BROKER_URL="amqp://guest:guest@localhost:5672//"
CELERY_RESULT_BACKEND="db+postgresql://user:password@localhost:5432/tradevantage"
```

### Avviare il Server
```bash
# Assicurati di essere nella directory backend/
source venv/bin/activate
uvicorn app.main:app --reload
```

### Avviare i Background Workers
```bash
# In un terminale separato
celery -A app.celery_app worker --loglevel=info -P solo -Q imports,celery
```

### Eseguire i Test
```bash
# Esegue tutti i test con coverage
pytest tests/
```

## 📂 Struttura del Progetto (Annotata)

```text
backend/
├── app/
│   ├── Controllers/                    # Gestori delle richieste & delega logica
│   │   ├── analytics_controller.py     # Logica statistiche aggregate
│   │   ├── import_controller.py        # Caricamento file & trigger task
│   │   ├── soa_controller.py           # Endpoint Strength & Opportunity Analysis
│   │   ├── trades_controller.py        # CRUD per i trade
│   │   └── ...
│   ├── Infrastructure/                 # Integrazioni servizi esterni
│   │   ├── db.py                       # Connessione DB & gestione sessioni
│   │   ├── storage.py                  # Wrapper client Supabase Storage
│   │   └── supabase_service.py         # Wrapper client Supabase Auth
│   ├── Middleware/                     # Middleware ASGI
│   │   └── security_headers.py         # Intestazioni di sicurezza (CORS, HSTS, ecc.)
│   ├── Models/                         # Modelli ORM SQLAlchemy (Schema Database)
│   │   ├── trade.py                    # Entità Trade principale
│   │   ├── playbook.py                 # Entità Playbook & Regole
│   │   ├── trading_dna.py              # Risultati analisi DNA
│   │   └── ...
│   ├── Repositories/                   # Livello Accesso Dati (CRUD)
│   │   ├── trade_repository.py         # Query complesse per i trade
│   │   ├── soa_repository.py           # Recupero dati per analisi
│   │   └── ...
│   ├── Router/                         # Definizioni Route API
│   │   ├── routes.py                   # Aggregatore router principale
│   │   ├── trades_router.py            # Endpoint per /trades
│   │   └── ...
│   ├── Schemas/                        # Modelli Pydantic (Validazione)
│   │   ├── trade.py                    # Schema Input/Output per Trades
│   │   ├── soa.py                      # Schema per risultati Analisi
│   │   └── ...
│   ├── Services/                       # Logica di Business Principale
│   │   ├── metrics/                    # Sottomodulo per motori di calcolo
│   │   ├── soa_service.py              # Logica Clustering & Analisi Stat (Pandas/Sklearn)
│   │   ├── import_service.py           # Orchestra processo importazione file
│   │   ├── mt5_parser.py               # Parser per file MetaTrader 5
│   │   ├── ninjatrader_parser.py       # Parser per file NinjaTrader 8
│   │   └── ...
│   ├── Utils/                          # Utilità condivise
│   │   └── pagination.py               # Helper per paginazione
│   ├── celery_app.py                   # Configurazione applicazione Celery
│   ├── config.py                       # Configurazione App (Pydantic Settings)
│   ├── main.py                         # Entry point applicazione FastAPI
│   └── tasks.py                        # Definizioni task Celery (Job asincroni)
├── tests/                              # Suite Pytest
│   ├── controllers/                    # Test integrazione per endpoint API
│   ├── services/                       # Unit test per logica di business
│   └── repositories/                   # Test integrazione DB
├── .env                                # Variabili d'ambiente (gitignored)
├── conftest.py                         # Fixture & config Pytest
├── requirements.txt                    # Dipendenze Python
└── README.md                           # Questo file
```
