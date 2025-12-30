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
│   │   ├── __init__.py                 # Init pacchetto Controller
│   │   ├── analytics_controller.py     # Logica statistiche aggregate
│   │   ├── asset_alias_controller.py   # Logica mapping asset
│   │   ├── asset_class_controller.py   # Gestione classi asset
│   │   ├── asset_controller.py         # Gestione asset
│   │   ├── asset_market_controller.py  # Gestione sessioni di mercato
│   │   ├── auth_controller.py          # Gestori autenticazione
│   │   ├── broker_controller.py        # Gestione broker
│   │   ├── general_account_controller.py # Gestione account utente
│   │   ├── import_controller.py        # Caricamento file & trigger task
│   │   ├── mistake_controller.py       # Logica tracciamento errori
│   │   ├── news_impact_controller.py   # Logica eventi impatto notizie
│   │   ├── news_impacts_group_controller.py # Raggruppamento impatto notizie
│   │   ├── note_template_controller.py # Template notebook
│   │   ├── notebook_controller.py      # Logica notebook & note
│   │   ├── platform_controller.py      # Gestione piattaforme trading
│   │   ├── playbook_controller.py      # Logica strategie playbook
│   │   ├── psychology_state_controller.py # Tracciamento stati psicologici
│   │   ├── roles_controller.py         # Gestione ruoli RBAC
│   │   ├── rule_playbook_controller.py # Logica regole playbook
│   │   ├── rules_group_playbook_controller.py # Raggruppamento regole
│   │   ├── soa_controller.py           # Endpoint Strength & Opportunity Analysis
│   │   ├── tag_controller.py           # Gestione tag
│   │   ├── tags_group_controller.py    # Raggruppamento tag
│   │   ├── trades_controller.py        # CRUD per i trade
│   │   ├── trading_account_controller.py # Gestione conti di trading
│   │   ├── trading_dna_controller.py   # Analisi Trading DNA
│   │   ├── user_dashboard_layout_controller.py # Persistenza layout dashboard
│   │   ├── user_roles_controller.py    # Associazione Utente-Ruolo
│   │   └── users_controller.py         # Gestione profili utente
│   ├── Infrastructure/                 # Integrazioni servizi esterni
│   │   ├── __init__.py                 # Init pacchetto Infrastructure
│   │   ├── db.py                       # Connessione DB & gestione sessioni
│   │   ├── storage.py                  # Wrapper client Supabase Storage
│   │   └── supabase_service.py         # Wrapper client Supabase Auth
│   ├── Middleware/                     # Middleware ASGI
│   │   └── security_headers.py         # Intestazioni di sicurezza (CORS, HSTS, ecc.)
│   ├── Models/                         # Modelli ORM SQLAlchemy (Schema Database)
│   │   ├── __init__.py                 # Init pacchetto Models
│   │   ├── asset.py                    # Entità Asset
│   │   ├── asset_alias.py              # Entità Alias Asset
│   │   ├── asset_class.py              # Entità Classe Asset
│   │   ├── asset_market.py             # Entità Sessione Mercato
│   │   ├── auth_user.py                # Entità Utente
│   │   ├── broker.py                   # Entità Broker
│   │   ├── broker_asset_class.py       # Relazione Broker-Asset
│   │   ├── broker_platform.py          # Relazione Broker-Piattaforma
│   │   ├── daily_rule_instance.py      # Tracciamento regole giornaliere
│   │   ├── discipline_rule.py          # Entità Regola Disciplina
│   │   ├── discipline_settings.py      # Configurazione Disciplina
│   │   ├── enums.py                    # Enumerazioni globali
│   │   ├── general_account.py          # Entità Account Generale
│   │   ├── image.py                    # Entità Immagine/Screenshot
│   │   ├── import_run.py               # Tracciamento job importazione
│   │   ├── manual_rule.py              # Entità Regola Manuale
│   │   ├── mistake.py                  # Entità Errore
│   │   ├── news_impact.py              # Entità Impatto Notizia
│   │   ├── news_impacts_group.py       # Entità Gruppo Impatto Notizia
│   │   ├── note.py                     # Entità Nota
│   │   ├── note_template.py            # Entità Template Nota
│   │   ├── notebook_folder.py          # Entità Cartella Notebook
│   │   ├── notes_note_templates.py     # Relazione Nota-Template
│   │   ├── platform.py                 # Entità Piattaforma Trading
│   │   ├── playbook.py                 # Entità Playbook
│   │   ├── psychology_state.py         # Entità Stato Psicologico
│   │   ├── role.py                     # Entità Ruolo
│   │   ├── rule_playbook.py            # Entità Regola Playbook
│   │   ├── rules_group_playbook.py     # Entità Gruppo Regole
│   │   ├── tag.py                      # Entità Tag
│   │   ├── tags_group.py               # Entità Gruppo Tag
│   │   ├── trade.py                    # Entità Trade principale
│   │   ├── trades_mistakes.py          # Relazione Trade-Errore
│   │   ├── trades_news_impacts.py      # Relazione Trade-Notizia
│   │   ├── trades_psychology.py        # Relazione Trade-Psicologia
│   │   ├── trades_tags.py              # Relazione Trade-Tag
│   │   ├── trading_account.py          # Entità Conto Trading
│   │   ├── user_dashboard_layout.py    # Entità Layout Dashboard
│   │   └── user_role.py                # Relazione Utente-Ruolo
│   ├── Repositories/                   # Livello Accesso Dati (CRUD)
│   │   ├── __init__.py                 # Init pacchetto Repositories
│   │   ├── asset_alias_repository.py   # Accesso alias asset
│   │   ├── asset_class_repository.py   # Accesso classi asset
│   │   ├── asset_market_repository.py  # Accesso mercati asset
│   │   ├── asset_repository.py         # Accesso asset
│   │   ├── auth_user_repository.py     # Accesso utenti
│   │   ├── base_repository.py          # Classe base repository generica
│   │   ├── broker_asset_class_repository.py # Accesso Broker-Asset
│   │   ├── broker_repository.py        # Accesso broker
│   │   ├── daily_rule_instance_repository.py # Accesso regole giornaliere
│   │   ├── discipline_settings_repository.py # Accesso impostazioni disciplina
│   │   ├── general_account_repository.py # Accesso account generale
│   │   ├── image_repository.py         # Accesso immagini
│   │   ├── manual_rule_repository.py   # Accesso regole manuali
│   │   ├── mistake_repository.py       # Accesso errori
│   │   ├── news_impact_repository.py   # Accesso impatto notizie
│   │   ├── news_impacts_group_repository.py # Accesso gruppi impatto notizie
│   │   ├── note_repository.py          # Accesso note
│   │   ├── note_template_repository.py # Accesso template note
│   │   ├── notebook_folder_repository.py # Accesso cartelle notebook
│   │   ├── platform_repository.py      # Accesso piattaforme
│   │   ├── playbook_repository.py      # Accesso playbook
│   │   ├── psychology_state_repository.py # Accesso stati psicologici
│   │   ├── role_repository.py          # Accesso ruoli
│   │   ├── rule_playbook_repository.py # Accesso regole playbook
│   │   ├── rules_group_playbook_repository.py # Accesso gruppi regole
│   │   ├── tag_repository.py           # Accesso tag
│   │   ├── tags_group_repository.py    # Accesso gruppi tag
│   │   ├── trade_repository.py         # Query complesse per i trade
│   │   ├── trading_account_repository.py # Accesso conti trading
│   │   ├── user_dashboard_layout_repository.py # Accesso layout dashboard
│   │   └── user_role_repository.py     # Accesso ruoli utente
│   ├── Router/                         # Definizioni Route API
│   │   ├── __init__.py                 # Init pacchetto Router
│   │   ├── analytics_router.py         # Route analitiche
│   │   ├── asset_alias_router.py       # Route alias asset
│   │   ├── asset_class_router.py       # Route classi asset
│   │   ├── asset_market_router.py      # Route mercati asset
│   │   ├── asset_router.py             # Route asset
│   │   ├── auth.py                     # Route autenticazione
│   │   ├── broker_router.py            # Route broker
│   │   ├── daily_checklist_router.py   # Route checklist giornaliera
│   │   ├── dependencies.py             # Dipendenze API (Auth, ecc.)
│   │   ├── discipline_settings_router.py # Route impostazioni disciplina
│   │   ├── general_account_router.py   # Route account generale
│   │   ├── image_router.py             # Route immagini
│   │   ├── import_router.py            # Route importazione
│   │   ├── manual_rule_router.py       # Route regole manuali
│   │   ├── mistake_router.py           # Route errori
│   │   ├── news_impact_router.py       # Route impatto notizie
│   │   ├── news_impacts_group_router.py # Route gruppi impatto notizie
│   │   ├── notebook_router.py          # Route notebook
│   │   ├── platform_router.py          # Route piattaforme
│   │   ├── playbook_router.py          # Route playbook
│   │   ├── psychology_state_router.py  # Route stati psicologici
│   │   ├── routes.py                   # Aggregatore router principale
│   │   ├── rule_playbook_router.py     # Route regole playbook
│   │   ├── rule_statistics_router.py   # Route statistiche regole
│   │   ├── rules_group_playbook_router.py # Route gruppi regole
│   │   ├── soa_router.py               # Route SOA
│   │   ├── tag_router.py               # Route tag
│   │   ├── tags_group_router.py        # Route gruppi tag
│   │   ├── trades_router.py            # Route trade
│   │   ├── trading_account_router.py   # Route conti trading
│   │   └── trading_dna_router.py       # Route Trading DNA
│   ├── Schemas/                        # Modelli Pydantic (Validazione)
│   │   ├── discipline/                 # Schemi annidati per disciplina
│   │   ├── __init__.py                 # Init pacchetto Schemas
│   │   ├── analytics.py                # Schemi analitici
│   │   ├── asset.py                    # Schemi asset
│   │   ├── asset_alias.py              # Schemi alias asset
│   │   ├── asset_class.py              # Schemi classi asset
│   │   ├── asset_market.py             # Schemi mercati asset
│   │   ├── auth_session.py             # Schemi sessione auth
│   │   ├── auth_user.py                # Schemi utente
│   │   ├── broker.py                   # Schemi broker
│   │   ├── broker_asset_class.py       # Schemi broker-asset
│   │   ├── daily_rule_instance_schema.py # Schemi regola giornaliera
│   │   ├── discipline_settings_schema.py # Schemi impostazioni disciplina
│   │   ├── general_account.py          # Schemi account generale
│   │   ├── image.py                    # Schemi immagine
│   │   ├── import_run.py               # Schemi esecuzione import
│   │   ├── manual_rule_schema.py       # Schemi regola manuale
│   │   ├── mistake.py                  # Schemi errore
│   │   ├── news_impact.py              # Schemi impatto notizia
│   │   ├── news_impacts_group.py       # Schemi gruppo impatto notizia
│   │   ├── note_template.py            # Schemi template nota
│   │   ├── notebook.py                 # Schemi notebook
│   │   ├── platform.py                 # Schemi piattaforma
│   │   ├── playbook.py                 # Schemi playbook
│   │   ├── psychology_state.py         # Schemi stato psicologico
│   │   ├── role.py                     # Schemi ruolo
│   │   ├── rule_playbook.py            # Schemi regola playbook
│   │   ├── rules_group_playbook.py     # Schemi gruppo regole
│   │   ├── soa.py                      # Schemi SOA
│   │   ├── stats.py                    # Schemi statistiche
│   │   ├── tag.py                      # Schemi tag
│   │   ├── tags_group.py               # Schemi gruppo tag
│   │   ├── trade.py                    # Schemi trade
│   │   ├── trades_tags.py              # Schemi trade-tag
│   │   ├── trading_account.py          # Schemi conto trading
│   │   ├── trading_dna.py              # Schemi Trading DNA
│   │   ├── user_dashboard_layout.py    # Schemi layout dashboard
│   │   ├── user_role.py                # Schemi ruolo utente
│   │   └── vantage_score.py            # Schemi punteggio vantage
│   ├── Services/                       # Logica di Business Principale
│   │   ├── metrics/                    # Motori calcolo metriche
│   │   ├── __init__.py                 # Init pacchetto Services
│   │   ├── analytics_service.py        # Logica di business analitica
│   │   ├── broker_service.py           # Logica broker
│   │   ├── discipline_settings_service.py # Logica disciplina
│   │   ├── general_account_service.py  # Logica account generale
│   │   ├── image_service.py            # Logica gestione immagini
│   │   ├── import_service.py           # Orchestrazione importazione
│   │   ├── jwt_service.py              # Gestione JWT
│   │   ├── mt5_parser.py               # Parsing file MT5
│   │   ├── ninjatrader_parser.py       # Parsing file NinjaTrader
│   │   ├── note_template_service.py    # Logica template nota
│   │   ├── notebook_service.py         # Logica notebook
│   │   ├── playbook_analytics_service.py # Analitiche playbook
│   │   ├── playbook_service.py         # Logica playbook
│   │   ├── role_service.py             # Logica ruoli
│   │   ├── rule_statistics_service.py  # Logica statistiche regole
│   │   ├── soa_advisor.py              # Generazione consigli SOA
│   │   ├── soa_service.py              # Motore calcolo SOA
│   │   ├── supabase_client.py          # Factory client Supabase
│   │   ├── trade_service.py            # Logica trade
│   │   ├── trading_account_service.py  # Logica conti trading
│   │   ├── trading_dna_service.py      # Logica Trading DNA
│   │   ├── tradovate_parser.py         # Parsing file Tradovate
│   │   ├── user_dashboard_layout_service.py # Logica dashboard
│   │   └── user_service.py             # Logica utente
│   ├── Utils/                          # Utilità condivise
│   │   ├── __init__.py                 # Init pacchetto Utils
│   │   └── pagination.py               # Helper per paginazione
│   ├── celery_app.py                   # Configurazione applicazione Celery
│   ├── config.py                       # Configurazione App (Pydantic Settings)
│   ├── main.py                         # Entry point applicazione FastAPI
│   └── tasks.py                        # Definizioni task Celery (Job asincroni)
├── tests/                              # Suite Pytest
│   ├── controllers/                    # Test integrazione per endpoint API
│   ├── repositories/                   # Test integrazione per Repositories
│   ├── services/                       # Unit test per Services
│   └── utils/                          # Unit test per Utilities
├── .env                                # Variabili d'ambiente (gitignored)
├── conftest.py                         # Fixture & config Pytest
├── requirements.txt                    # Dipendenze Python
└── README.md                           # Questo file
```
