# uvicorn_config.py
from uvicorn.config import LOGGING_CONFIG

# Disabilita i ping WebSocket non necessari che possono causare ritardi
ws_ping_interval = None
ws_ping_timeout = None

# Usa una configurazione di logging più pulita
log_config = LOGGING_CONFIG
log_config["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
log_config["formatters"]["access"]["fmt"] = '%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'

# Impostazioni per disabilitare la risoluzione DNS inversa (indirettamente tramite il formato di log)
# e per un avvio più pulito.
bind = "0.0.0.0:8000"
workers = 1
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
